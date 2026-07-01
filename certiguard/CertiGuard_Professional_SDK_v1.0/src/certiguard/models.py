from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    code: str
    message: str
    metadata: dict[str, Any]

