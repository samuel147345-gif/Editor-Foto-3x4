# -*- coding: utf-8 -*-
"""
Processamento híbrido Python + C# otimizado
Fallback automático e uso inteligente de recursos
"""
import io
from PIL import Image, ImageEnhance, ImageOps
from typing import List, Optional
from .cs_bridge import get_cs_bridge, is_cs_available

def enforce_3x4(box, img_size):
    """Força proporção 3:4 com clamp de limites"""
    x0, y0, x1, y1 = box
    img_w, img_h = img_size
    
    # Clamp inicial
    x0, y0 = max(0, min(x0, img_w)), max(0, min(y0, img_h))
    x1, y1 = max(0, min(x1, img_w)), max(0, min(y1, img_h))
    
    w, h = x1 - x0, y1 - y0
    target = 3/4
    
    # Ajusta proporção
    if w / h > target:
        new_w = int(h * target)
        cx = (x0 + x1) // 2
        x0, x1 = cx - new_w // 2, cx + new_w // 2
    else:
        new_h = int(w / target)
        cy = (y0 + y1) // 2
        y0, y1 = cy - new_h // 2, cy + new_h // 2
    
    # Clamp final
    x0, y0 = max(0, min(x0, img_w)), max(0, min(y0, img_h))
    x1, y1 = max(0, min(x1, img_w)), max(0, min(y1, img_h))
    
    return (int(x0), int(y0), int(x1), int(y1))

def apply_image_enhancements(image, contrast=1.0, brightness=1.0, quality=100, use_cs=True):
    """Aplica melhorias com fallback automático"""
    
    # Tenta C# se disponível e imagem tem arquivo
    if use_cs and is_cs_available() and hasattr(image, 'filename') and image.filename:
        try:
            bridge = get_cs_bridge()
            brightness_offset = (brightness - 1.0) * 100
            
            result = bridge.apply_image_filters(
                image.filename,
                contrast=contrast,
                brightness=brightness_offset
            )
            
            if result.get('Success'):
                processed = Image.open(result['OutputPath'])
                
                if quality < 100:
                    buffer = io.BytesIO()
                    processed.save(buffer, format='JPEG', quality=quality)
                    buffer.seek(0)
                    processed = Image.open(buffer)
                
                return processed
        except Exception as e:
            print(f"Fallback Python: {e}")
    
    # Fallback Python
    img = ImageEnhance.Contrast(image).enhance(contrast)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    
    if quality < 100:
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        img = Image.open(buffer)
    
    return img

def resize_image(image, scale_factor, use_cs=True):
    """Redimensiona imagem"""
    nw = max(1, int(image.width * scale_factor))
    nh = max(1, int(image.height * scale_factor))
    return image.resize((nw, nh), Image.LANCZOS)

def batch_resize_images(paths: List[str], scales: List[float], use_cs=True) -> List[Optional[str]]:
    """Redimensiona múltiplas imagens com C# ou Python"""
    
    if use_cs and is_cs_available() and len(paths) > 1:
        try:
            bridge = get_cs_bridge()
            result = bridge.batch_resize_images(paths, scales)
            
            if 'Results' in result:
                return [r['OutputPath'] if r.get('Success') else None 
                       for r in result['Results']]
        except Exception as e:
            print(f"Fallback Python: {e}")
    
    # Fallback Python
    outputs = []
    for path, scale in zip(paths, scales):
        try:
            with Image.open(path) as img:
                resized = resize_image(img, scale, use_cs=False)
                output = path.replace('.', '_resized.')
                resized.save(output)
                outputs.append(output)
        except Exception as e:
            print(f"Erro: {e}")
            outputs.append(None)
    
    return outputs

def add_border(image, border_width=5, border_color="black"):
    """Adiciona borda"""
    return ImageOps.expand(image, border=border_width, fill=border_color)

def compute_initial_scale(img, canvas_w, canvas_h):
    """Calcula escala inicial"""
    if canvas_w < 10 or canvas_h < 10:
        canvas_w, canvas_h = 800, 650
    return min(canvas_w / img.width, canvas_h / img.height, 1.0)

def get_performance_info():
    """Info sobre componentes de performance"""
    return {
        "cs_available": is_cs_available(),
        "hybrid_mode": True,
        "components": ["Python PIL", "C# SkiaSharp"] if is_cs_available() else ["Python PIL"]
    }