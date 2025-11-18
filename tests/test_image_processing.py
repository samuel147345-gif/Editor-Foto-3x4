# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.image_processing import enforce_3x4, compute_initial_scale

def test_enforce_3x4_basic():
    result = enforce_3x4((0, 0, 300, 400), (800, 600))
    assert len(result) == 4

def test_compute_initial_scale():
    """Testa cálculo de escala inicial"""
    from PIL import Image
    img = Image.new('RGB', (800, 600))
    scale = compute_initial_scale(img, 640, 480)
    
    assert isinstance(scale, (int, float))
    assert 0 < scale <= 1.0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])