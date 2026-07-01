from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SecurityPolicy:
    require_tpm_if_present: bool = False
    allow_vm: bool = True
    exe_hash_grace_hours: int = 72
    baseline_learning_days: int = 30
    anomaly_enforcement_after_learning: bool = True
    # When True, L6 uses ``behavior_probe`` (CPU/RAM/process/GPU hints) instead of caller-supplied floats.
    use_machine_behavior_probe: bool = False

    @classmethod
    def load(cls, path: Path | None = None) -> "SecurityPolicy":
        if path is None or not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{k: data[k] for k in cls.__dataclass_fields__.keys() if k in data})

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")

