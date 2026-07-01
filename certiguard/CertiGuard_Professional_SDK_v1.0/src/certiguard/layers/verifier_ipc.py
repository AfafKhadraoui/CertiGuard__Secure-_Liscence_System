from __future__ import annotations

import base64
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from certiguard.layers.verifier_server import verify_license_and_respond


def _socket_path(state_dir: Path) -> Path:
    return state_dir / "license_verifier.sock"


def verify_via_separate_process(
    *,
    state_dir: Path,
    license_path: Path,
    public_key_path: Path,
    challenge_nonce: bytes,
    app_binary_path: Path | None,
    exe_hash_grace_hours: int,
) -> dict[str, Any]:
    if not hasattr(socket, "AF_UNIX"):
        return verify_license_and_respond(
            license_path=license_path,
            public_key_path=public_key_path,
            challenge_nonce=challenge_nonce,
            dna_path=state_dir / "dna.json",
            counter_path=state_dir / "counter.json",
            app_binary_path=app_binary_path,
            grace_state_path=state_dir / "integrity_grace.json",
            exe_hash_grace_hours=exe_hash_grace_hours,
        )
    sock_path = _socket_path(state_dir)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "certiguard.verifier_daemon",
            "--state-dir",
            str(state_dir),
            "--public-key",
            str(public_key_path),
        ]
    )
    try:
        for _ in range(30):
            if sock_path.exists():
                break
            time.sleep(0.05)
        if not sock_path.exists():
            raise TimeoutError("Verifier process did not open IPC socket")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(sock_path))
            req = {
                "license_path": str(license_path),
                "challenge_nonce_b64": base64.b64encode(challenge_nonce).decode("ascii"),
                "app_binary_path": str(app_binary_path) if app_binary_path else None,
                "exe_hash_grace_hours": exe_hash_grace_hours,
            }
            client.sendall(json.dumps(req).encode("utf-8"))
            raw = client.recv(131072)
        resp = json.loads(raw.decode("utf-8"))
        if not resp.get("ok"):
            raise PermissionError(resp.get("error", "Verifier rejected request"))
        return resp["response"]
    finally:
        proc.wait(timeout=5)
