from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature
import os


def canonical_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def generate_keypair(private_path: Path, public_path: Path) -> None:
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(
        private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def load_private_key(path: Path) -> Ed25519PrivateKey:
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def load_public_key(path: Path) -> Ed25519PublicKey:
    return serialization.load_pem_public_key(path.read_bytes())


def sign_payload(payload: dict[str, Any], private_key: Ed25519PrivateKey) -> bytes:
    payload_bytes = canonical_payload(payload)
    sig = private_key.sign(payload_bytes)
    return sig + payload_bytes


def sign_payload_bytes(payload_bytes: bytes, private_key: Ed25519PrivateKey) -> bytes:
    sig = private_key.sign(payload_bytes)
    return sig + payload_bytes


def verify_payload(signed_bytes: bytes, public_key: Ed25519PublicKey) -> bytes:
    if len(signed_bytes) < 64:
        raise InvalidSignature("Payload too short to contain signature")
    sig = signed_bytes[:64]
    payload_bytes = signed_bytes[64:]
    public_key.verify(sig, payload_bytes)
    return payload_bytes


def derive_key_hkdf(salt: bytes, ikm: bytes, info: bytes, length: int = 32) -> bytes:
    """
    Derive a key using HKDF-SHA256.
    Matches the logic used in ShieldWrap for cryptographic dependency.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info,
    )
    return hkdf.derive(ikm)


def encrypt_binary(key: bytes, plaintext: bytes) -> bytes:
    """
    Encrypt binary data using AES-256-GCM.
    Output format: nonce(12) || ciphertext(N) || tag(16)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    # cryptography's AESGCM.encrypt returns ciphertext + tag
    ct_with_tag = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ct_with_tag


def decrypt_binary(key: bytes, ciphertext_blob: bytes) -> bytes:
    """
    Decrypt binary data using AES-256-GCM.
    Input format: nonce(12) || ciphertext(N) || tag(16)
    """
    if len(ciphertext_blob) < 28:
        raise ValueError("Ciphertext blob too short")
    
    nonce = ciphertext_blob[:12]
    ct_with_tag = ciphertext_blob[12:]
    
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct_with_tag, None)

