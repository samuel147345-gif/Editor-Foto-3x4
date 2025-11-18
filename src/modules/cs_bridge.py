# -*- coding: utf-8 -*-
"""
Módulo de ponte Python-C# otimizado
Comunicação via JSON/subprocess com cache otimizado e fallback automático
"""
import json
import subprocess
import os
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache
from collections import OrderedDict

logger = logging.getLogger(__name__)

class LRUCache:
    """Cache LRU (Least Recently Used) com limite de tamanho e tempo"""
    
    def __init__(self, max_size=100, ttl_seconds=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.timestamps = {}
    
    def get(self, key):
        """Obtém item do cache se válido"""
        if key not in self.cache:
            return None
        
        # Verifica TTL
        if time.time() - self.timestamps[key] > self.ttl:
            self.delete(key)
            return None
        
        # Move para o fim (mais recente)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key, value):
        """Adiciona item ao cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove o mais antigo
                oldest = next(iter(self.cache))
                self.delete(oldest)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def delete(self, key):
        """Remove item do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self):
        """Retorna tamanho atual"""
        return len(self.cache)
    
    def cleanup_expired(self):
        """Remove itens expirados"""
        current_time = time.time()
        expired = [
            key for key, timestamp in self.timestamps.items()
            if current_time - timestamp > self.ttl
        ]
        for key in expired:
            self.delete(key)


class CSharpBridge:
    """Ponte Python-C# com cache otimizado e validação"""
    
    def __init__(self):
        self.cs_executable = self._find_cs_executable()
        self.available = self.cs_executable is not None
        # Cache LRU com máximo 100 itens, TTL 5 minutos
        self._cache = LRUCache(max_size=100, ttl_seconds=300)
        
        if self.available:
            logger.info(f"C# disponível: {self.cs_executable}")
        else:
            logger.warning("C# não disponível - usando fallback Python")
    
    @lru_cache(maxsize=1)
    def _find_cs_executable(self) -> Optional[str]:
        """Localiza executável C# em caminhos estratégicos"""
        base = Path(__file__).parent.parent
        
        paths = [
            base / "FastImageOps.exe",
            base / "cs_components" / "FastImageOps" / "bin" / "Release" / "net8.0" / "win-x64" / "publish" / "FastImageOps.exe",
            base / "modules" / "cs_dlls" / "FastImageOps.exe",
            base.parent / "cs_components" / "FastImageOps" / "bin" / "Release" / "net8.0" / "win-x64" / "publish" / "FastImageOps.exe"
        ]
        
        for path in paths:
            if path.exists():
                return str(path)
        return None
    
    def _execute(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa operação C# com timeout e validação"""
        if not self.available:
            raise RuntimeError("C# não disponível")
        
        # Limpa cache expirado periodicamente
        if self._cache.size() > 50:
            self._cache.cleanup_expired()
        
        # Verifica cache
        cache_key = f"{operation}:{json.dumps(data, sort_keys=True)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit: {operation}")
            return cached
        
        try:
            json_input = json.dumps(data, ensure_ascii=False)
            cmd = [self.cs_executable, operation, json_input]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                check=False
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Erro C#: {result.stderr}")
            
            response = json.loads(result.stdout)
            
            # Adiciona ao cache
            self._cache.set(cache_key, response)
            logger.debug(f"Cache miss: {operation} (cache size: {self._cache.size()})")
            
            return response
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout C# (30s)")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"JSON inválido: {e}")
        except Exception as e:
            raise RuntimeError(f"Erro comunicação C#: {e}")
    
    def batch_resize_images(self, paths: List[str], scales: List[float]) -> Dict[str, Any]:
        """Redimensiona múltiplas imagens"""
        return self._execute("batch-resize", {
            "Images": [{"Path": p, "Scale": s} for p, s in zip(paths, scales)]
        })
    
    def apply_image_filters(self, path: str, contrast: float = 1.0, 
                           brightness: float = 0.0) -> Dict[str, Any]:
        """Aplica filtros de imagem"""
        return self._execute("apply-filters", {
            "ImagePath": path,
            "Contrast": contrast,
            "Brightness": brightness
        })
    
    def batch_crop_images(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Crop em lote"""
        return self._execute("batch-crop", {"Images": images})
    
    def clear_cache(self):
        """Limpa cache de operações"""
        self._cache.clear()
        logger.info("Cache C# limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "size": self._cache.size(),
            "max_size": self._cache.max_size,
            "ttl_seconds": self._cache.ttl
        }

# Instância singleton
_bridge = CSharpBridge()

def get_cs_bridge() -> CSharpBridge:
    """Retorna instância da ponte C#"""
    return _bridge

def is_cs_available() -> bool:
    """Verifica disponibilidade C#"""
    return _bridge.available
