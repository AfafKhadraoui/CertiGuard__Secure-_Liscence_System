from __future__ import annotations

from certiguard.layers.hardware import get_machine_uuid


def test_get_machine_uuid_uses_argument_lists(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_check_output(cmd):
        calls.append(list(cmd))
        if cmd[:4] == ["wmic", "csproduct", "get", "uuid"]:
            return b"UUID\nABCDEF-1234\n"
        if cmd[:3] == ["ioreg", "-rd1", "-c"]:
            return b'    "IOPlatformUUID" = "MAC-UUID-1234"\n'
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr("certiguard.layers.hardware.subprocess.check_output", fake_check_output)

    monkeypatch.setattr("certiguard.layers.hardware.platform.system", lambda: "Windows")
    assert get_machine_uuid() == "ABCDEF-1234"

    monkeypatch.setattr("certiguard.layers.hardware.platform.system", lambda: "Darwin")
    assert get_machine_uuid() == "MAC-UUID-1234"

    assert calls == [
        ["wmic", "csproduct", "get", "uuid"],
        ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
    ]