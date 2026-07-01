from __future__ import annotations

import base64
import hashlib
import os
import json
from pathlib import Path
from certiguard.layers.crypto_core import encrypt_binary

def protect_executable(
    *,
    exe_path: Path,
    out_dir: Path,
) -> dict:
    """
    Encrypts an executable with a random key (K_app).
    Returns the K_app and BINARY_SECRET which must be passed to the CA
    to generate the license-wrapped key.
    """
    if not exe_path.exists():
        raise FileNotFoundError(f"Executable not found: {exe_path}")

    # 1. Read and hash original binary
    data = exe_path.read_bytes()
    app_hash = hashlib.sha256(data).hexdigest()
    
    # 2. Generate secrets
    binary_secret = os.urandom(32)
    k_app = os.urandom(32)
    
    # 3. Encrypt binary
    encrypted_data = encrypt_binary(k_app, data)
    
    # 4. Save results
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "app.enc").write_bytes(encrypted_data)
    
    protection_metadata = {
        "app_hash": app_hash,
        "app_size": len(data),
        "binary_secret_b64": base64.b64encode(binary_secret).decode("ascii"),
        "k_app_b64": base64.b64encode(k_app).decode("ascii"),
    }
    
    # We save a partial manifest that the CA will complete
    manifest = {
        "app_hash": app_hash,
        "app_size": len(data),
        "binary_secret_b64": protection_metadata["binary_secret_b64"],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    
    return protection_metadata
