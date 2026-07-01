from __future__ import annotations

import json
import base64
import os
import subprocess
import tempfile
import hashlib
from datetime import UTC, datetime
from pathlib import Path

from certiguard.config import SecurityPolicy
from certiguard.layers.anomaly import BehaviorDetector
from certiguard.layers.behavior_probe import probe_host_behavior, probe_to_feature_vector
from certiguard.layers.antidebug import debugger_detected
from certiguard.layers.antivm import is_virtual_machine
from certiguard.layers.audit import append_event, verify_chain
from certiguard.layers.counter import ensure_boot_counter, init_counter
from certiguard.layers.dna import capture_runtime_snapshot, init_installation_dna, load_installation_dna
from certiguard.layers.hardware import generate_hardware_fingerprint
from certiguard.layers.tpm import tpm_anchor, tpm_info
from certiguard.layers.verifier_ipc import verify_via_separate_process
from certiguard.layers.verifier_server import random_challenge, verify_challenge_response
from certiguard.layers.watchdog import verify_heartbeat_recent, write_heartbeat
from certiguard.layers.crypto_core import load_private_key, sign_payload, verify_payload, load_public_key, derive_key_hkdf, decrypt_binary
from certiguard.layers.storage import secure_write_json
from certiguard.layers.sync import SyncManager
from certiguard.models import VerificationResult


class CertiGuardClient:
    """
    Local state (including tamper-evident audit.log) is always written first.
    When ``CERTIGUARD_COLLECTOR_URL`` or ``collector_url`` is set, verification
    and renewal export also attempt to push unsynced audit lines to the dashboard
    ingest API (best-effort; failures are ignored so offline operation continues).
    """

    def __init__(self, state_dir: Path, *, collector_url: str | None = None) -> None:
        self.state_dir = state_dir
        self.dna_path = state_dir / "dna.json"
        self.counter_path = state_dir / "counter.json"
        self.audit_path = state_dir / "audit.log"
        self.heartbeat_path = state_dir / "heartbeat.json"
        self.grace_path = state_dir / "integrity_grace.json"
        self.baseline_state_path = state_dir / "behavior_baseline.json"
        self.policy_path = state_dir / "policy.json"
        if collector_url is not None:
            self._collector_url = str(collector_url).strip()
        else:
            self._collector_url = (os.environ.get("CERTIGUARD_COLLECTOR_URL") or "").strip()

    def collector_configured(self) -> bool:
        return bool(self._collector_url)

    def push_audit_logs_now(self) -> bool:
        """Send unsynced lines from ``audit.log`` to the collector (``/api/logs/ingest``)."""
        if not self._collector_url:
            return False
        return SyncManager(self.state_dir, self._collector_url).sync_now(self.audit_path)

    def _try_push_audit_logs(self) -> None:
        try:
            self.push_audit_logs_now()
        except Exception:
            pass

    def bootstrap(self) -> dict:
        hw_fp = generate_hardware_fingerprint()
        init_installation_dna(self.dna_path, hw_fp)
        init_counter(self.counter_path, hw_fp)
        runtime = capture_runtime_snapshot()
        boot_count = ensure_boot_counter(self.counter_path, hw_fp, runtime["boot_id"])
        dna = load_installation_dna(self.dna_path, hw_fp)
        req = {
            "generated_at": datetime.now(UTC).isoformat(),
            "hardware_fingerprint": hw_fp,
            "install_dna": {**dna, "boot_count_at_issue": boot_count},
        }
        anchor = tpm_anchor()
        req["tpm"] = {"available": bool(anchor), "anchor": anchor, "info": tpm_info()}
        return req

    def verify_runtime(
        self,
        *,
        license_path: Path,
        public_key_path: Path,
        heartbeat_key: str,
        behavior_features: list[float],
        require_tpm_if_present: bool = False,
        app_binary_path: Path | None = None,
        policy_path: Path | None = None,
        use_machine_behavior_probe: bool = False,
    ) -> VerificationResult:
        def _run() -> VerificationResult:
            policy = SecurityPolicy.load(policy_path or self.policy_path)
            require_tpm = require_tpm_if_present or policy.require_tpm_if_present
            if debugger_detected():
                append_event(self.audit_path, "debug_detected", {})
                return VerificationResult(False, "L5_DEBUG", "Debugger detected", {})

            if not policy.allow_vm and is_virtual_machine():
                append_event(self.audit_path, "vm_detected", {})
                return VerificationResult(False, "L5_VM", "Virtual Machine environment blocked by policy", {})

            if not verify_chain(self.audit_path):
                return VerificationResult(False, "AUDIT_TAMPER", "Audit chain invalid", {})

            challenge = random_challenge()
            try:
                runtime = capture_runtime_snapshot()
                ensure_boot_counter(self.counter_path, generate_hardware_fingerprint(), runtime["boot_id"])
                response = verify_via_separate_process(
                    state_dir=self.state_dir,
                    license_path=license_path,
                    public_key_path=public_key_path,
                    challenge_nonce=challenge,
                    app_binary_path=app_binary_path,
                    exe_hash_grace_hours=policy.exe_hash_grace_hours,
                )
            except Exception as exc:
                append_event(self.audit_path, "license_reject", {"reason": str(exc)})
                return VerificationResult(False, "L1_L4_REJECT", str(exc), {})

            if not verify_challenge_response(
                response["hmac_response"],
                license_path=license_path,
                challenge_nonce=challenge,
                dna_path=self.dna_path,
                counter_path=self.counter_path,
            ):
                append_event(self.audit_path, "challenge_fail", {})
                return VerificationResult(False, "L4_CHALLENGE", "Challenge-response failed", {})

            write_heartbeat(self.heartbeat_path, heartbeat_key)
            if not verify_heartbeat_recent(self.heartbeat_path, heartbeat_key):
                append_event(self.audit_path, "heartbeat_stale", {})
                return VerificationResult(False, "L5_DMS", "Verifier heartbeat invalid", {})

            # Optional premium tier check: if license includes TPM anchor, enforce it.
            raw_bytes = base64.b64decode(license_path.read_text(encoding="ascii"))
            payload_bytes = raw_bytes[64:]
            lic = json.loads(payload_bytes.decode("utf-8"))
            lic_tpm = lic.get("tpm", {})
            expected_anchor = lic_tpm.get("anchor")
            local_anchor = tpm_anchor()
            if expected_anchor:
                if local_anchor != expected_anchor:
                    append_event(self.audit_path, "tpm_mismatch", {"expected_bound": bool(expected_anchor)})
                    return VerificationResult(False, "L2_TPM", "TPM anchor mismatch", {})
            elif require_tpm and local_anchor:
                append_event(self.audit_path, "tpm_policy_fail", {"require_tpm": True})
                return VerificationResult(False, "L2_TPM_POLICY", "TPM present but not bound in license", {})

            probe_enabled = bool(use_machine_behavior_probe) or bool(policy.use_machine_behavior_probe)
            probe_snapshot: dict | None = None
            if probe_enabled:
                probe_snapshot = probe_host_behavior()
                effective_features = probe_to_feature_vector(probe_snapshot)
                feature_source = "machine_probe"
            else:
                effective_features = list(behavior_features)
                feature_source = "application"

            detector = BehaviorDetector(baseline_state_path=self.baseline_state_path)
            is_anomaly, score = detector.score(effective_features)
            baseline = detector.update_customer_baseline(
                effective_features, learning_days=policy.baseline_learning_days
            )
            drift, drift_score = detector.detect_drift(effective_features)
            behavior_payload: dict = {
                "anomaly": is_anomaly,
                "score": score,
                "drift": drift,
                "drift_score": drift_score,
                "learning_complete": baseline.get("learning_complete", False),
                "feature_source": feature_source,
                "feature_dim": len(effective_features),
            }
            if probe_snapshot is not None:
                behavior_payload["behavior_probe"] = {
                    "cpu_percent": probe_snapshot.get("cpu_percent"),
                    "cpu_logical": probe_snapshot.get("cpu_logical"),
                    "mem_percent": probe_snapshot.get("mem_percent"),
                    "process_count": probe_snapshot.get("process_count"),
                    "display_adapter_count": probe_snapshot.get("display_adapter_count"),
                    "gpu_discrete_class_hint": probe_snapshot.get("gpu_discrete_class_hint"),
                    "nvidia_smi_gpu_lines": probe_snapshot.get("nvidia_smi_gpu_lines"),
                    "explanation": probe_snapshot.get("explanation", "")[:2000],
                }
            append_event(self.audit_path, "behavior_check", behavior_payload)
            
            # PASSIVE MONITORING: We log the anomaly but return OK=True.
            # This ensures legitimate users aren't blocked by performance spikes.
            # The Vendor can see the 'is_anomaly' flag in the Dashboard.
            return VerificationResult(
                True,
                "OK_WITH_ANOMALY" if (is_anomaly or drift) else "OK",
                "License accepted (Behavioral Warning logged)" if (is_anomaly or drift) else "License accepted",
                {
                    "anomaly": is_anomaly,
                    "score": score,
                    "drift": drift,
                    "license_id": response["license_id"],
                    "feature_source": feature_source,
                },
            )

        try:
            return _run()
        finally:
            self._try_push_audit_logs()

    def export_renewal_request(self, out_path: Path, customer_private_key_path: Path | None = None) -> None:
        payload = {
            "request_type": "renewal",
            "generated_at": datetime.now(UTC).isoformat(),
            "audit_chain_valid": verify_chain(self.audit_path),
            "audit_log": self.audit_path.read_text(encoding="utf-8") if self.audit_path.exists() else "",
            "dna": json.loads(self.dna_path.read_text(encoding="utf-8")) if self.dna_path.exists() else {},
            "counter": json.loads(self.counter_path.read_text(encoding="utf-8")) if self.counter_path.exists() else {},
        }
        if customer_private_key_path:
            payload["customer_signature"] = sign_payload(payload, load_private_key(customer_private_key_path))
        secure_write_json(out_path, payload)
        self._try_push_audit_logs()

    def run_protected_app(
        self,
        *,
        package_dir: Path,
        license_path: Path,
        public_key_path: Path,
        skip_layered_verify: bool = False,
        heartbeat_key: str | None = None,
        behavior_features: list[float] | None = None,
        require_tpm_if_present: bool = False,
        app_binary_path: Path | None = None,
        policy_path: Path | None = None,
        use_machine_behavior_probe: bool = False,
    ) -> int:
        """
        Executes a protected application using the ShieldWrap cryptographic flow.

        Unless ``skip_layered_verify=True``, runs the same ``verify_runtime`` stack
        **before any decryption** (L5 anti-debug → L10 chain → L4 verifier → L5 heartbeat
        → L2 TPM policy → L6 behavior). If verification fails, the binary is never
        decrypted and this returns exit code **2**.

        Cryptographic steps after verification (when enabled and successful):

        1. Verify license signature (again, as part of L4 / ShieldWrap inputs).
        2. Derive decryption key (K_derived) from license + manifest.
        3. Decrypt application key (K_app).
        4. Decrypt application binary.
        5. Execute in a secure temporary environment.
        """
        if not skip_layered_verify:
            if heartbeat_key is None or behavior_features is None:
                raise ValueError(
                    "run_protected_app requires heartbeat_key and behavior_features "
                    "unless skip_layered_verify=True (full stack runs before decrypt)"
                )
            vr = self.verify_runtime(
                license_path=license_path,
                public_key_path=public_key_path,
                heartbeat_key=heartbeat_key,
                behavior_features=behavior_features,
                require_tpm_if_present=require_tpm_if_present,
                app_binary_path=app_binary_path,
                policy_path=policy_path,
                use_machine_behavior_probe=use_machine_behavior_probe,
            )
            if not vr.ok:
                # Audit lines are already written inside verify_runtime for most codes;
                # exit 2 ensures the encrypted binary is never decrypted.
                return 2

        # 1. Load and verify license
        raw_lic_bytes = base64.b64decode(license_path.read_text(encoding="ascii"))
        public_key = load_public_key(public_key_path)
        payload_bytes = verify_payload(raw_lic_bytes, public_key)
        lic = json.loads(payload_bytes.decode("utf-8"))

        # 2. Load manifest
        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("Package manifest.json missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        # 3. Derive K_derived (The Cryptographic Dependency)
        shieldwrap = lic.get("shieldwrap")
        if not shieldwrap:
            raise ValueError("License does not contain ShieldWrap protection data")
        
        seed = base64.b64decode(lic["seed_b64"])
        binary_secret = base64.b64decode(shieldwrap["binary_secret_b64"])
        
        # Build IKM using LOCAL hardware fingerprint + LOCAL TPM anchor (if license is bound)
        local_hwid = generate_hardware_fingerprint()
        ikm_str = f"{local_hwid}|{lic['valid_until']}"
        
        # If the license expects a TPM anchor, we MUST provide our local one for the math to work.
        if lic.get("tpm", {}).get("anchor"):
            from certiguard.layers.tpm import tpm_anchor as get_tpm_anchor
            local_tpm = get_tpm_anchor()
            if local_tpm:
                ikm_str += f"|{local_tpm}"
            # If no local TPM but license is bound, ikm_str won't match CA's, so decryption will fail.

        ikm = ikm_str.encode("utf-8") + binary_secret
        k_derived = derive_key_hkdf(
            salt=seed,
            ikm=ikm,
            info=b"certiguard-v3-kdf"
        )

        # 4. Decrypt K_app
        encrypted_k_app = base64.b64decode(shieldwrap["encrypted_key_b64"])
        try:
            k_app = decrypt_binary(k_derived, encrypted_k_app)
        except Exception:
            raise ValueError("Failed to decrypt application key - license/hardware mismatch")

        # 5. Decrypt Application Binary
        enc_app_path = package_dir / "app.enc"
        if not enc_app_path.exists():
            raise FileNotFoundError("Encrypted application binary (app.enc) missing")
        
        enc_app_data = enc_app_path.read_bytes()
        dec_app_data = decrypt_binary(k_app, enc_app_data)

        # 6. Integrity check
        actual_hash = hashlib.sha256(dec_app_data).hexdigest()
        if actual_hash != manifest["app_hash"]:
            raise ValueError("Application integrity check failed after decryption")

        # 7. Secure Execution
        # We write to a temp file, run it, then wipe it.
        temp_exe = Path(tempfile.gettempdir()) / f"cg_{os.getpid()}.exe"
        try:
            temp_exe.write_bytes(dec_app_data)
            print(f"[*] Launching protected application...")
            result = subprocess.run([str(temp_exe)], check=False)
            return result.returncode
        finally:
            # Secure wipe (overwrite with zeros) before deletion
            if temp_exe.exists():
                temp_exe.write_bytes(os.urandom(len(dec_app_data)))
                temp_exe.unlink()

