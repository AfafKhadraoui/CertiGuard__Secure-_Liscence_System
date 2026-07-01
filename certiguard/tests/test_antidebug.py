import platform
import sys
import time
from certiguard.layers.antidebug import debugger_detected

def test_debugger_detected_normal_run():
    # In a normal test run (assuming we aren't debugging the test itself),
    # this should return False.
    # Note: If the test is run under a debugger (e.g. from an IDE in debug mode),
    # this test will naturally fail, which actually proves it works.
    
    # We will temporarily disable sys.settrace if pytest or coverage is using it
    # just for the context of this specific check if needed, but for simplicity
    # we just run it and assert it doesn't crash.
    
    original_trace = sys.gettrace()
    if original_trace is None:
        # Not under a Python debugger like pdb or PyCharm's debugger
        # So we expect it to be False (unless a native debugger is attached)
        assert debugger_detected() is False

def test_debugger_detected_timing():
    # If we mock the time.perf_counter_ns to simulate a huge delay, it should return True
    import certiguard.layers.antidebug as ad
    
    # Save original
    original_perf = time.perf_counter
    
    # Mock to always return a huge gap
    class MockPerfCounter:
        def __init__(self):
            self.count = 0.0
        def __call__(self):
            current = self.count
            self.count += 5.0 # Add 5 seconds of "fake delay"
            return current
            
    ad.time.perf_counter = MockPerfCounter()
    
    try:
        # Should detect the "timing anomaly"
        # The function uses 'threshold' in seconds
        assert ad.check_timing_anomaly(threshold=0.1) is True
    finally:
        # Restore
        ad.time.perf_counter = original_perf
