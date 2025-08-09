#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE CONFIGURACIÓN FASE 1.6 MULTI-PAR
Script para verificar que la configuración multi-par esté funcionando correctamente
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config_fase_1_6 import config
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    sys.exit(1)

def test_multi_par_config():
    """Probar configuración multi-par"""
    print("🔍 Verificando configuración FASE 1.6 MULTI-PAR...")
    print("=" * 60)
    
    # Verificar símbolos
    print(f"📊 Símbolos configurados: {', '.join(config.SYMBOLS)}")
    print(f"🎯 Símbolo actual: {config.get_current_symbol()}")
    
    # Verificar rotación
    print("\n🔄 Probando rotación de símbolos:")
    for i in range(8):
        symbol = config.get_current_symbol()
        print(f"  Ciclo {i+1}: {symbol}")
        config.rotate_symbol()
    
    # Verificar configuración bloqueada
    print("\n🔒 Verificando configuración V1 bloqueada:")
    print(f"  TP_MIN_BPS: {config.TP_MIN_BPS} bps")
    print(f"  TP_BUFFER_BPS: {config.TP_BUFFER_BPS} bps")
    print(f"  MIN_RANGE_BPS: {config.MIN_RANGE_BPS} bps")
    print(f"  MAX_SPREAD_BPS: {config.MAX_SPREAD_BPS} bps")
    print(f"  MIN_VOL_USD: ${config.MIN_VOL_USD:,.0f}")
    print(f"  ATR_MIN_PCT: {config.ATR_MIN_PCT}%")
    print(f"  MAX_TRADES_PER_DAY: {config.MAX_TRADES_PER_DAY}")
    print(f"  DAILY_MAX_DRAWDOWN_PCT: {config.DAILY_MAX_DRAWDOWN_PCT}%")
    
    # Verificar validación
    print("\n✅ Validando configuración:")
    if config.validate_config():
        print("  ✅ Configuración válida")
    else:
        print("  ❌ Configuración inválida")
        return False
    
    return True

def test_tp_floor_calculation():
    """Probar cálculo de TP floor"""
    print("\n🎯 Probando cálculo de TP floor:")
    
    # Calcular fricción
    fee_bps = max(config.FEE_TAKER_BPS, config.FEE_MAKER_BPS)
    fric_bps = 2 * fee_bps + config.SLIPPAGE_BPS
    tp_floor = fric_bps + config.TP_BUFFER_BPS
    
    print(f"  Fee máximo: {fee_bps} bps")
    print(f"  Fricción total: {fric_bps} bps")
    print(f"  TP buffer: {config.TP_BUFFER_BPS} bps")
    print(f"  TP floor: {tp_floor} bps")
    print(f"  TP mínimo: {config.TP_MIN_BPS} bps")
    
    if config.TP_MIN_BPS >= tp_floor:
        print("  ✅ TP mínimo >= TP floor")
        return True
    else:
        print("  ❌ TP mínimo < TP floor")
        return False

def test_symbol_prices():
    """Probar precios simulados por símbolo"""
    print("\n💰 Probando precios por símbolo:")
    
    import random
    
    prices = {}
    for symbol in config.SYMBOLS:
        if symbol == 'BTCUSDT':
            price = random.uniform(40000, 50000)
        elif symbol == 'ETHUSDT':
            price = random.uniform(2000, 3000)
        elif symbol == 'BNBUSDT':
            price = random.uniform(500, 650)
        elif symbol == 'SOLUSDT':
            price = random.uniform(80, 120)
        else:
            price = random.uniform(500, 650)
        
        prices[symbol] = price
        print(f"  {symbol}: ${price:,.2f}")
    
    return prices

def test_daily_summary():
    """Probar resumen diario"""
    print("\n📊 Probando resumen diario:")
    
    # Simular datos de trades
    daily_trades = [
        {'result': 'GANANCIA', 'net_pnl': 0.0010, 'capital': 50.001},
        {'result': 'PÉRDIDA', 'net_pnl': -0.0005, 'capital': 50.0005},
        {'result': 'GANANCIA', 'net_pnl': 0.0020, 'capital': 50.0025},
    ]
    
    total_trades = len(daily_trades)
    winning_trades = len([t for t in daily_trades if t.get('result') == 'GANANCIA'])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    gains = sum([t.get('net_pnl', 0) for t in daily_trades if t.get('net_pnl', 0) > 0])
    losses = abs(sum([t.get('net_pnl', 0) for t in daily_trades if t.get('net_pnl', 0) < 0]))
    profit_factor = gains / losses if losses > 0 else (gains if gains > 0 else 0)
    
    daily_pnl_net = sum([t.get('net_pnl', 0) for t in daily_trades])
    
    print(f"  Trades: {total_trades}")
    print(f"  Ganados: {winning_trades}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Profit Factor: {profit_factor:.2f}")
    print(f"  P&L Neto: ${daily_pnl_net:.4f}")
    
    return True

def main():
    """Función principal"""
    print("🚀 VERIFICADOR FASE 1.6 MULTI-PAR")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar pruebas
    tests = [
        ("Configuración Multi-Par", test_multi_par_config),
        ("Cálculo TP Floor", test_tp_floor_calculation),
        ("Precios por Símbolo", test_symbol_prices),
        ("Resumen Diario", test_daily_summary),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Configuración lista para producción.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
