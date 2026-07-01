"""Smoke tests for L6 machine behavior probe + 6-D anomaly path."""

import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from certiguard.layers.anomaly import BehaviorDetector
from certiguard.layers.behavior_probe import probe_host_behavior, probe_to_feature_vector


def test_probe_returns_six_floats():
    raw = probe_host_behavior()
    vec = probe_to_feature_vector(raw)
    assert len(vec) == 6
    assert all(isinstance(x, float) for x in vec)
    assert "explanation" in raw


def test_detector_six_dim_roundtrip(tmp_path):
    p = tmp_path / "baseline.json"
    d = BehaviorDetector(baseline_state_path=p)
    v = probe_to_feature_vector(
        {
            "cpu_percent": 22.0,
            "cpu_logical": 8,
            "mem_percent": 55.0,
            "process_count": 200,
            "gpu_discrete_class_hint": 1,
            "nvidia_smi_gpu_lines": 0,
            "display_adapter_count": 2,
            "hour_local": 14,
        }
    )
    an, sc = d.score(v)
    assert isinstance(an, bool)
    assert isinstance(sc, float)
    st = d.update_customer_baseline(v, learning_days=2)
    assert st["sessions"] == 1
    assert st["feature_dim"] == 6
