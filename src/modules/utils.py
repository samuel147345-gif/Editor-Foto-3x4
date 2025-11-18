"""
Módulo de utilitários
Contém funções auxiliares e helpers
"""
import os

def get_image_name_from_path(path):
    """
    Extrai nome do arquivo de um caminho completo
    """
    return os.path.basename(path)

def validate_image_format(format_type):
    """
    Valida se o formato de imagem é suportado
    """
    supported_formats = ["JPEG", "PNG", "BMP", "TIFF"]
    return format_type in supported_formats

def clamp_value(value, min_val, max_val):
    """
    Limita valor entre mínimo e máximo
    """
    return max(min_val, min(value, max_val))

def safe_division(numerator, denominator, default=0):
    """
    Divisão segura que evita divisão por zero
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def format_file_size(size_bytes):
    """
    Formata tamanho de arquivo em formato legível
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_bundle_dir():
    """
    Retorna diretório do bundle para arquivos empacotados
    """
    import sys
    return getattr(sys, '_MEIPASS', os.path.dirname(__file__))
