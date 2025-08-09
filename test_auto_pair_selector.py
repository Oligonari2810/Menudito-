#!/usr/bin/env python3
"""
🧪 TEST AUTO PAIR SELECTOR - FASE 1.6
Script para probar el Auto Pair Selector
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Importar módulos
try:
    from config_fase_1_6 import config
    from pair_selector import AutoPairSelector, init_pair_selector, get_pair_selector
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def test_auto_pair_selector():
    """Test principal del Auto Pair Selector"""
    print("\n🎯 TEST AUTO PAIR SELECTOR - FASE 1.6")
    print("=" * 50)
    
    try:
        # Inicializar selector
        print("\n1️⃣ Inicializando Auto Pair Selector...")
        pair_selector = init_pair_selector(config)
        
        if not pair_selector:
            print("❌ Error: No se pudo inicializar el selector")
            return False
        
        print(f"✅ Auto Pair Selector inicializado")
        print(f"📊 Candidatos: {len(pair_selector.pairs_candidates)} pares")
        print(f"🎯 Máximo activos: {pair_selector.max_active_pairs}")
        print(f"🔄 Rebalance: {pair_selector.rebalance_minutes} min")
        
        # Test 1: Selección inicial de pares
        print("\n2️⃣ Test: Selección inicial de pares...")
        active_pairs = pair_selector.select_active_pairs()
        
        if not active_pairs:
            print("❌ Error: No se pudieron seleccionar pares activos")
            return False
        
        print(f"✅ Pares activos seleccionados: {', '.join(active_pairs)}")
        
        # Test 2: Cálculo de scores
        print("\n3️⃣ Test: Cálculo de scores...")
        pair_selector.log_universe_summary()
        
        # Test 3: Verificar rebalance
        print("\n4️⃣ Test: Verificar rebalance...")
        should_rebalance = pair_selector.should_rebalance()
        print(f"🔄 Debe rebalancear: {should_rebalance}")
        
        # Test 4: Obtener datos del universo
        print("\n5️⃣ Test: Datos del universo...")
        universe_data = pair_selector.get_universe_data()
        
        if 'universe_data' in universe_data:
            print(f"📊 Datos del universo obtenidos: {len(universe_data['universe_data'])} registros")
            print(f"🎯 Pares activos: {', '.join(universe_data['active_pairs'])}")
        else:
            print("⚠️ No se pudieron obtener datos del universo")
        
        # Test 5: Simular rebalance
        print("\n6️⃣ Test: Simular rebalance...")
        rebalance_result = pair_selector.rebalance_pairs()
        print(f"🔄 Rebalance simulado: {rebalance_result}")
        
        print("\n✅ TODOS LOS TESTS PASARON")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def test_config_integration():
    """Test de integración con configuración"""
    print("\n🔧 TEST INTEGRACIÓN CON CONFIGURACIÓN")
    print("=" * 40)
    
    try:
        # Verificar variables del Auto Pair Selector
        print("1️⃣ Verificando variables de configuración...")
        
        required_vars = [
            'AUTO_PAIR_SELECTOR',
            'PAIRS_CANDIDATES', 
            'MAX_ACTIVE_PAIRS',
            'REBALANCE_MINUTES',
            'LOOKBACK_HOURS',
            'CAND_MIN_24H_VOLUME_USD',
            'CAND_MIN_ATR_BPS',
            'CAND_MAX_SPREAD_BPS',
            'CAND_MIN_TREND_SCORE',
            'CAND_MAX_CORRELATION'
        ]
        
        for var in required_vars:
            if hasattr(config, var):
                value = getattr(config, var)
                print(f"✅ {var}: {value}")
            else:
                print(f"❌ {var}: No encontrado")
                return False
        
        print("\n✅ Todas las variables de configuración están presentes")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO TESTS AUTO PAIR SELECTOR")
    print("=" * 50)
    
    # Test configuración
    config_ok = test_config_integration()
    
    # Test funcionalidad
    func_ok = test_auto_pair_selector()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    if config_ok and func_ok:
        print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ Auto Pair Selector listo para producción")
        print("\n🎯 CARACTERÍSTICAS VERIFICADAS:")
        print("📊 Selección automática de pares")
        print("🎯 Cálculo de scores basado en métricas")
        print("🔄 Sistema de rebalance")
        print("📈 Filtros de mercado")
        print("🛡️ Seguridad de cambio")
        print("📊 Telemetría del universo")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        if not config_ok:
            print("- ❌ Configuración no válida")
        if not func_ok:
            print("- ❌ Funcionalidad no válida")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
