# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.cs_bridge import get_cs_bridge, is_cs_available
from modules.image_processing_hybrid import enforce_3x4, get_performance_info

def test_cs_bridge_availability():
    bridge = get_cs_bridge()
    assert bridge is not None
    assert hasattr(bridge, 'available')

def test_enforce_3x4_proportions():
    result = enforce_3x4((0, 0, 300, 400), (800, 600))
    w, h = result[2] - result[0], result[3] - result[1]
    assert abs(w/h - 0.75) < 0.01

def test_performance_info():
    info = get_performance_info()
    assert 'cs_available' in info

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])