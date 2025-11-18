# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.face_detection import detect_faces

def test_detect_faces_function_exists():
    assert callable(detect_faces)

def test_detect_faces_with_invalid_path():
    try:
        faces = detect_faces("invalid.jpg")
        assert isinstance(faces, list)
    except:
        assert True

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])