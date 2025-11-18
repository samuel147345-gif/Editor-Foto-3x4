# -*- coding: utf-8 -*-
"""
Editor de Fotos 3×4 - Módulos
Arquitetura modular híbrida Python + C#
Versão 3.1.0
"""

__version__ = "3.1.0"
__author__ = "Samuel Fernandes"

# Imports principais para facilitar uso
from .cs_bridge import get_cs_bridge, is_cs_available
from .file_manager import FileManager
from .utils import get_image_name_from_path

__all__ = [
    'get_cs_bridge',
    'is_cs_available',
    'FileManager',
    'get_image_name_from_path'
]
