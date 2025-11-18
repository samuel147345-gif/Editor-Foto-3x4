# -*- coding: utf-8 -*-
"""
Módulo de processamento de imagem
Contém todas as operações de manipulação de imagem
"""
import io
from PIL import Image, ImageEnhance, ImageOps

def enforce_3x4(box, img_size):
    """
    Recebe box=(x0,y0,x1,y1) e img_size=(img_w,img_h),
    primeiro clampa a box dentro da imagem e só então força
    a proporção 3:4 centralizando.
    """
    x0, y0, x1, y1 = box
    img_w, img_h = img_size

    x0 = max(0, min(x0, img_w))
    y0 = max(0, min(y0, img_h))
    x1 = max(0, min(x1, img_w))
    y1 = max(0, min(y1, img_h))

    w, h = x1 - x0, y1 - y0
    target = 3/4

    if w / h > target:
        new_w = int(h * target)
        cx = (x0 + x1) // 2
        x0 = cx - new_w // 2
        x1 = cx + new_w // 2
    else:
        new_h = int(w / target)
        cy = (y0 + y1) // 2
        y0 = cy - new_h // 2
        y1 = cy + new_h // 2
        
    x0 = max(0, min(x0, img_w))
    y0 = max(0, min(y0, img_h))
    x1 = max(0, min(x1, img_w))
    y1 = max(0, min(y1, img_h))

    return (int(x0), int(y0), int(x1), int(y1))

def apply_image_enhancements(image, contrast=1.0, brightness=1.0, quality=100):
    """
    Aplica melhorias de contraste, brilho e qualidade à imagem
    """
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    
    if quality < 100:
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        image = Image.open(buffer)
    
    return image

def resize_image(image, scale_factor):
    """
    Redimensiona a imagem com o fator de escala especificado
    """
    nw = max(1, int(image.width * scale_factor))
    nh = max(1, int(image.height * scale_factor))
    return image.resize((nw, nh), Image.LANCZOS)

def add_border(image, border_width=5, border_color="black"):
    """
    Adiciona borda à imagem
    """
    return ImageOps.expand(image, border=border_width, fill=border_color)

def compute_initial_scale(pil_img, canvas_width, canvas_height):
    """
    Calcula escala inicial para ajustar imagem ao canvas
    """
    if canvas_width < 10 or canvas_height < 10:
        canvas_width, canvas_height = 800, 650
    return min(canvas_width / pil_img.width, canvas_height / pil_img.height, 1.0)
