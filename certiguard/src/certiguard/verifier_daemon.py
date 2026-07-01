from __future__ import annotations

import argparse
import base64
import json
import socket
from pathlib import Path

from certiguard.layers.verifier_server import verify_license_and_respond


def _socket_path(state_dir: Path) -> str:
    if hasattr(socket, "AF_UNIX"):
        return str(state_dir / "license_verifier.sock")
    return ""


def run_once(state_dir: Path, public_key_path: Path) -> None:
    sock_path = _socket_path(state_dir)
    if not sock_path:
        raise RuntimeError("Unix domain sockets are required for verifier daemon")
    sock_file = Path(sock_path)
    if sock_file.exists():
        sock_file.unlink()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(1)
    try:
        conn, _ = server.accept()
        with conn:
            raw = conn.recv(131072)
            req = json.loads(raw.decode("utf-8"))
            try:
                result = verify_license_and_respond(
                    license_path=Path(req["license_path"]),
                    public_key_path=public_key_path,
                    challenge_nonce=base64.b64decode(req["challenge_nonce_b64"]),
                    dna_path=state_dir / "dna.json",
                    counter_path=state_dir / "counter.json",
                    app_binary_path=Path(req["app_binary_path"]) if req.get("app_binary_path") else None,
                    grace_state_path=state_dir / "integrity_grace.json",
                    exe_hash_grace_hours=int(req.get("exe_hash_grace_hours", 72)),
                )
                conn.sendall(json.dumps({"ok": True, "response": result}).encode("utf-8"))
            except Exception as exc:
                conn.sendall(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"))
    finally:
        server.close()
        if sock_file.exists():
            sock_file.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(prog="certiguard-verifier-daemon")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--public-key", required=True)
    args = parser.parse_args()
    run_once(Path(args.state_dir), Path(args.public_key))


if __name__ == "__main__":
    main()
