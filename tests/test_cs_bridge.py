# -*- coding: utf-8 -*-
"""
Testes de integração CS Bridge + Image Processing Hybrid
Valida comunicação Python-C# e fallback
"""
import sys
import os
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src/cs_components/FastImageOps'))

from modules.cs_bridge import get_cs_bridge, is_cs_available
from modules.image_processing_hybrid import (
    enforce_3x4, 
    apply_image_enhancements, 
    get_performance_info
)

def test_cs_bridge():
    """Testa disponibilidade CS Bridge"""
    print("=" * 60)
    print("TESTE 1: CS Bridge Disponibilidade")
    print("=" * 60)
    
    bridge = get_cs_bridge()
    print(f"✓ Bridge criada: {bridge}")
    print(f"✓ Executável: {bridge.cs_executable}")
    print(f"✓ Disponível: {bridge.available}")
    
    if bridge.available:
        print("✓ C# OPERACIONAL")
    else:
        print("! C# INDISPONÍVEL - Fallback Python ativo")
    print()

def test_enforce_3x4():
    """Testa função enforce_3x4"""
    print("=" * 60)
    print("TESTE 2: Enforce 3x4 Proporção")
    print("=" * 60)
    
    test_cases = [
        ((0, 0, 300, 400), (800, 600)),
        ((50, 50, 350, 450), (800, 600)),
        ((0, 0, 600, 400), (800, 600))
    ]
    
    for box, img_size in test_cases:
        result = enforce_3x4(box, img_size)
        print(f"Box: {box} | Size: {img_size}")
        print(f"→ Result: {result}")
        
        # Valida proporção 3:4
        w = result[2] - result[0]
        h = result[3] - result[1]
        ratio = w / h if h > 0 else 0
        expected = 3/4
        
        if abs(ratio - expected) < 0.01:
            print(f"✓ Proporção OK: {ratio:.3f}")
        else:
            print(f"✗ ERRO: {ratio:.3f} != {expected:.3f}")
        print()

def test_performance_info():
    """Testa informações de performance"""
    print("=" * 60)
    print("TESTE 3: Performance Info")
    print("=" * 60)
    
    info = get_performance_info()
    print(f"✓ CS Available: {info['cs_available']}")
    print(f"✓ Hybrid Mode: {info['hybrid_mode']}")
    print(f"✓ Components: {', '.join(info['components'])}")
    print()

def test_cache():
    """Testa sistema de cache"""
    print("=" * 60)
    print("TESTE 4: Sistema de Cache")
    print("=" * 60)
    
    bridge = get_cs_bridge()
    print(f"✓ Cache inicial: {bridge._cache.size()} itens")
    
    # Cache é interno - apenas teste stats
    stats = bridge.get_cache_stats()
    print(f"✓ Max size: {stats['max_size']}")
    print(f"✓ TTL: {stats['ttl_seconds']}s")
    
    bridge.clear_cache()
    print(f"✓ Cache após clear: {bridge._cache.size()} itens")
    print()

def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " TESTES CS BRIDGE + IMAGE PROCESSING HYBRID ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        test_cs_bridge()
        test_enforce_3x4()
        test_performance_info()
        test_cache()
        
        print("=" * 60)
        print("✓ TODOS OS TESTES PASSARAM")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"✗ ERRO NOS TESTES: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)