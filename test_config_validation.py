#!/usr/bin/env python3
"""
🧪 TEST: Validación de configuración FASE 1.6
Verifica que todos los parámetros de configuración sean válidos
"""

import sys
import os
from typing import Dict, Any, List, Optional

def test_config_import():
    """Test 1: Verificar que se puede importar la configuración"""
    try:
        from config_fase_1_6 import config
        print("✅ Configuración importada correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando configuración: {e}")
        return False

def test_config_validation():
    """Test 2: Verificar validación de configuración"""
    try:
        from config_fase_1_6 import config
        
        # Validar TP mínimo > fricción
        fee_bps = max(config.FEE_TAKER_BPS, config.FEE_MAKER_BPS)
        fric_bps = 2 * fee_bps + config.SLIPPAGE_BPS
        tp_floor = fric_bps + config.TP_BUFFER_BPS
        
        if config.TP_MIN_BPS < tp_floor:
            print(f"❌ TP_MIN_BPS ({config.TP_MIN_BPS}) < tp_floor ({tp_floor})")
            return False
        
        print(f"✅ TP mínimo: {config.TP_MIN_BPS} bps >= floor {tp_floor} bps")
        
        # Validar filtros
        if config.MIN_RANGE_BPS <= 0:
            print(f"❌ MIN_RANGE_BPS debe ser > 0")
            return False
        
        if config.MAX_SPREAD_BPS <= 0:
            print(f"❌ MAX_SPREAD_BPS debe ser > 0")
            return False
        
        if config.MIN_VOL_USD <= 0:
            print(f"❌ MIN_VOL_USD debe ser > 0")
            return False
        
        # Validar latencia
        if config.MAX_WS_LATENCY_MS <= 0:
            print(f"❌ MAX_WS_LATENCY_MS debe ser > 0")
            return False
        
        if config.MAX_REST_LATENCY_MS <= 0:
            print(f"❌ MAX_REST_LATENCY_MS debe ser > 0")
            return False
        
        print(f"✅ Filtros y latencia válidos")
        return True
        
    except Exception as e:
        print(f"❌ Error validando configuración: {e}")
        return False

def test_config_values():
    """Test 3: Verificar valores específicos de configuración"""
    try:
        from config_fase_1_6 import config
        
        expected_values = {
            'FEE_TAKER_BPS': 7.5,
            'FEE_MAKER_BPS': 2.0,
            'SLIPPAGE_BPS': 1.5,
            'TP_BUFFER_BPS': 2.0,
            'TP_MODE': 'fixed_min',
            'TP_MIN_BPS': 18.5,
            'MIN_RANGE_BPS': 5.0,
            'MAX_SPREAD_BPS': 2.0,
            'MIN_VOL_USD': 5000000,
            'MAX_WS_LATENCY_MS': 1500,
            'MAX_REST_LATENCY_MS': 800
        }
        
        for key, expected_value in expected_values.items():
            actual_value = getattr(config, key)
            if actual_value != expected_value:
                print(f"❌ {key}: {actual_value} != {expected_value}")
                return False
            else:
                print(f"✅ {key}: {actual_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando valores: {e}")
        return False

def test_config_summary():
    """Test 4: Verificar resumen de configuración"""
    try:
        from config_fase_1_6 import config
        
        summary = config.get_config_summary()
        required_keys = [
            'mode', 'live_trading', 'shadow_mode', 'symbol',
            'position_percent', 'tp_mode', 'tp_min_bps',
            'min_range_bps', 'max_spread_bps', 'min_vol_usd',
            'max_ws_latency_ms', 'max_rest_latency_ms',
            'fee_taker_bps', 'fee_maker_bps', 'slippage_bps'
        ]
        
        for key in required_keys:
            if key not in summary:
                print(f"❌ Falta clave en resumen: {key}")
                return False
        
        print(f"✅ Resumen de configuración válido")
        print(f"📊 Resumen: {summary}")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando resumen: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Test: Validación de configuración FASE 1.6")
    print("=" * 50)
    
    tests = [
        ("Import de configuración", test_config_import),
        ("Validación de configuración", test_config_validation),
        ("Valores específicos", test_config_values),
        ("Resumen de configuración", test_config_summary)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    print(f"📈 Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡Configuración FASE 1.6 válida!")
        return 0
    else:
        print(f"\n❌ {total - passed} tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
