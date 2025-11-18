# -*- coding: utf-8 -*-
"""
Módulo de detecção facial - CORRIGIDO UTF-8
Suporte para caminhos com acentos no Windows
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image

def get_cascade_path():
    """
    Busca o arquivo haarcascade em múltiplos locais
    CORRIGIDO: Prioriza locais mais confiáveis
    """
    # 1. Tentar OpenCV data (ambiente de desenvolvimento)
    cv_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if os.path.exists(cv_path):
        return cv_path
    
    # 2. Tentar pasta _MEIPASS (PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        meipass_path = os.path.join(sys._MEIPASS, 'haarcascade_frontalface_default.xml')
        if os.path.exists(meipass_path):
            return meipass_path
    
    # 3. Tentar pasta do executável
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        exe_path = os.path.join(exe_dir, 'haarcascade_frontalface_default.xml')
        if os.path.exists(exe_path):
            return exe_path
    
    # 4. Tentar pasta do módulo
    module_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(module_dir, 'haarcascade_frontalface_default.xml')
    if os.path.exists(module_path):
        return module_path
    
    # 5. Tentar raiz do projeto
    root_path = os.path.join(os.path.dirname(module_dir), '..', 'haarcascade_frontalface_default.xml')
    root_path = os.path.abspath(root_path)
    if os.path.exists(root_path):
        return root_path
    
    return None

def get_cascade_classifier():
    """
    Retorna CascadeClassifier carregado ou None
    """
    cascade_path = get_cascade_path()
    
    if not cascade_path:
        raise FileNotFoundError(
            "haarcascade_frontalface_default.xml não encontrado.\n"
            "Verifique se o arquivo existe na instalação."
        )
    
    detector = cv2.CascadeClassifier(cascade_path)
    
    if detector.empty():
        raise RuntimeError(
            f"Falha ao carregar haarcascade de: {cascade_path}\n"
            "Arquivo pode estar corrompido."
        )
    
    return detector

def load_image_opencv(image_path):
    """
    Carrega imagem com suporte UTF-8/acentos
    
    Args:
        image_path: Caminho da imagem (suporta acentos)
    
    Returns:
        Imagem OpenCV (BGR) ou None se falhar
    """
    try:
        img_array = np.fromfile(image_path, dtype=np.uint8)
        img_cv = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img_cv
    except Exception:
        return None

def detect_faces(image_path):
    """
    Detecta todas as faces em uma imagem
    Retorna lista de coordenadas (x, y, w, h)
    """
    if not os.path.exists(image_path):
        return []
    
    img_cv = load_image_opencv(image_path)
    if img_cv is None:
        return []
    
    try:
        detector = get_cascade_classifier()
    except (FileNotFoundError, RuntimeError):
        return []
    
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    return faces.tolist() if len(faces) > 0 else []

def expand_and_pad_face_crop(path, pad_ratio=1.0):
    """
    Detecta face e retorna imagem cropada com proporção 3:4
    
    Args:
        path: Caminho da imagem (suporta acentos)
        pad_ratio: Razão de padding (1.0 = 100% do tamanho da face)
    
    Returns:
        PIL Image cropada ou None se não detectar
    """
    from .image_processing import enforce_3x4
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    
    img_cv = load_image_opencv(path)
    if img_cv is None:
        raise ValueError(f"Não foi possível carregar: {path}")
    
    try:
        detector = get_cascade_classifier()
    except (FileNotFoundError, RuntimeError) as e:
        raise RuntimeError(f"Erro ao carregar detector facial: {str(e)}")
    
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    if len(faces) == 0:
        return None
    
    x, y, w, h = faces[0]
    
    img_h, img_w = img_cv.shape[:2]
    
    pad_w = int(w * pad_ratio)
    pad_h = int(h * pad_ratio)
    
    x0 = max(0, x - pad_w // 2)
    y0 = max(0, y - pad_h // 2)
    x1 = min(img_w, x + w + pad_w // 2)
    y1 = min(img_h, y + h + pad_h // 2)
    
    box_3x4 = enforce_3x4((x0, y0, x1, y1), (img_w, img_h))
    
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    
    pil_img = Image.fromarray(img_rgb)
    return pil_img.crop(box_3x4)