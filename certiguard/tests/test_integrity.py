import time
import sys
from pathlib import Path

# Add src to sys.path to allow direct execution
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    import pytest
except ImportError:
    pytest = None

from certiguard.layers.integrity import check_integrity, file_sha256

def test_integrity_match(tmp_path):
    # Create a dummy executable file
    exe = tmp_path / "app.exe"
    exe.write_bytes(b"test data")
    
    expected_hash = file_sha256(exe)
    
    # Should pass
    assert check_integrity(exe, expected_hash) is True

def test_integrity_mismatch_grace_period(tmp_path):
    # Create a dummy executable file
    exe = tmp_path / "app.exe"
    exe.write_bytes(b"test data")
    
    expected_hash = "wrong hash"
    
    # First check: should return True but log a warning (Grace Window starts)
    assert check_integrity(exe, expected_hash) is True
    
    # If we modify the grace period constant or wait (not practical for unit test)
    # but we can verify it doesn't immediately fail.

def test_integrity_recovery(tmp_path):
    exe = tmp_path / "app.exe"
    exe.write_bytes(b"original")
    correct_hash = file_sha256(exe)
    
    # Tamper with it
    exe.write_bytes(b"tampered")
    assert check_integrity(exe, correct_hash) is True # Still in grace
    
    # Restore it
    exe.write_bytes(b"original")
    assert check_integrity(exe, correct_hash) is True # Back to normal

if __name__ == "__main__":
    if pytest:
        sys.exit(pytest.main([__file__]))
    else:
        import tempfile
        print("Running tests without pytest...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            test_integrity_match(tmp_path)
            test_integrity_mismatch_grace_period(tmp_path)
            test_integrity_recovery(tmp_path)
        print("All tests passed!")
