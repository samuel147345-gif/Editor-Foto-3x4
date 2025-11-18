# -*- coding: utf-8 -*-
"""
Gerenciador de configurações persistentes
"""
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path.home() / ".editor_fotos_3x4" / "config.json"

DEFAULT_CONFIG = {
    "border_enabled": False,
    "border_width": 5,
    "border_color": "black"
}

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo"""
        if not self.config_file.exists():
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    
    def save(self, config: Dict[str, Any]):
        """Salva configurações no arquivo"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
    
    def get(self, key: str, default=None):
        """Obtém valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Define valor de configuração"""
        self.config[key] = value
        self.save(self.config)
    
    def update(self, values: Dict[str, Any]):
        """Atualiza múltiplos valores"""
        self.config.update(values)
        self.save(self.config)

_config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    return _config_manager
