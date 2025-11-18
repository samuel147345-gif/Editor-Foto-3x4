# -*- coding: utf-8 -*-
"""
Sistema de logging estruturado
"""
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name="EditorFoto3x4"):
    """Configura logger com arquivo diário"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    log_dir = Path.home() / '.editor_fotos_3x4' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger