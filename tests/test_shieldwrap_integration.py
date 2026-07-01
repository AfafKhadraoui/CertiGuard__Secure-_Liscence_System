import json
import os
import subprocess
import pytest
from pathlib import Path
from certiguard.license_client import CertiGuardClient
from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair
from certiguard.layers.protector import protect_executable

def test_shieldwrap_cryptographic_dependency(tmp_path: Path):
    # 1. Setup keys
    keys_dir = tmp_path / "keys"
    priv_key = keys_dir / "vendor_priv.pem"
    pub_key = keys_dir / "vendor_pub.pem"
    generate_keypair(priv_key, pub_key)

    # 2. Create a dummy executable
    hello_c = tmp_path / "hello.c"
    hello_c.write_text('#include <stdio.h>\nint main() { printf("SUCCESS\\n"); return 0; }', encoding="utf-8")
    hello_exe = tmp_path / "hello.exe"
    
    # Compile it
    subprocess.run(["gcc", str(hello_c), "-o", str(hello_exe)], check=True)
    assert hello_exe.exists()

    # 3. Protect the executable
    package_dir = tmp_path / "protected_package"
    protection_metadata = protect_executable(
        exe_path=hello_exe,
        out_dir=package_dir
    )
    
    # 4. Bootstrap client and request license
    state_dir = tmp_path / "client_state"
    client = CertiGuardClient(state_dir)
    request = client.bootstrap()
    req_path = tmp_path / "request.json"
    req_path.write_text(json.dumps(request), encoding="utf-8")
    
    # 5. Issue License (linking it to the protection metadata)
    license_path = tmp_path / "license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_key,
        out_path=license_path,
        issued_to="TestUser",
        max_users=1,
        modules=["test"],
        valid_days=30,
        exe_hash=protection_metadata["app_hash"],
        k_app_b64=protection_metadata["k_app_b64"],
        binary_secret_b64=protection_metadata["binary_secret_b64"]
    )
    
    # 6. Run protected app (Should Succeed)
    print("\n--- Running with VALID license ---")
    ret_code = client.run_protected_app(
        package_dir=package_dir,
        license_path=license_path,
        public_key_path=pub_key
    )
    assert ret_code == 0
    
    # 7. Test Mismatch: Tamper with license (Should Fail Decryption)
    # If we change the HWID in the license, K_derived will be wrong, 
    # and AES-GCM will fail the authentication tag check.
    import base64
    raw_lic = base64.b64decode(license_path.read_text(encoding="ascii"))
    sig = raw_lic[:64]
    payload = json.loads(raw_lic[64:].decode("utf-8"))
    
    # Backup valid payload for another test
    valid_payload = payload.copy()
    
    # Tamper with HWID
    payload["hardware_fingerprint"] = "WRONG_HWID"
    # Note: We aren't even re-signing here. The Decryption will fail BEFORE 
    # the signature check if we bypass the signature check, OR the signature 
    # check will fail first.
    # But in run_protected_app, verify_payload is called first.
    # So to test decryption failure specifically, we'd need to bypass signature check 
    # or have a "valid" signature for a "wrong" HWID (e.g. issued for another PC).
    
    # Let's simulate a license issued for ANOTHER machine (validly signed)
    other_license_path = tmp_path / "other_machine.lic"
    # Modify request to have wrong HWID
    request_other = request.copy()
    request_other["hardware_fingerprint"] = "OTHER_PC_123"
    req_other_path = tmp_path / "req_other.json"
    req_other_path.write_text(json.dumps(request_other), encoding="utf-8")
    
    issue_license(
        request_path=req_other_path,
        private_key_path=priv_key,
        out_path=other_license_path,
        issued_to="TestUser",
        max_users=1,
        modules=["test"],
        valid_days=30,
        exe_hash=protection_metadata["app_hash"],
        k_app_b64=protection_metadata["k_app_b64"],
        binary_secret_b64=protection_metadata["binary_secret_b64"]
    )
    
    print("\n--- Running with license for DIFFERENT machine ---")
    with pytest.raises(ValueError, match="Failed to decrypt application key"):
        client.run_protected_app(
            package_dir=package_dir,
            license_path=other_license_path,
            public_key_path=pub_key
        )
    print("[+] Decryption correctly failed due to hardware mismatch")
