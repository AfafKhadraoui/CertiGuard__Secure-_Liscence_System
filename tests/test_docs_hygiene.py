from __future__ import annotations

from pathlib import Path


def test_canonical_docs_do_not_reference_stale_install_or_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target_files = [
        repo_root / "README.md",
        repo_root / "certiguard" / "README.md",
        repo_root / "docs" / "DEVELOPMENT_METHODOLOGY.md",
        repo_root / "docs" / "CertiGuard_Final_Implementation.md",
    ]

    content = "\n".join(path.read_text(encoding="utf-8") for path in target_files)

    assert "PyNaCl" not in content
    assert "nothingggg_us" not in content
    assert "pip install PyNaCl" not in content