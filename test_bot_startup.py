#!/usr/bin/env python3
"""
🧪 Script de prueba para verificar el inicio del bot
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_environment():
    """Verificar variables de entorno"""
    print("🔍 Verificando variables de entorno...")
    
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY', 
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Configurado")
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        return False
    else:
        print("✅ Todas las variables de entorno están configuradas")
        return True

def test_imports():
    """Verificar imports"""
    print("\n📦 Verificando imports...")
    
    try:
        from config_survivor_final import FinalSurvivorTradingConfig
        print("✅ Configuración importada")
        
        from modules.binance_client import BinanceTradingClient
        print("✅ Cliente Binance importado")
        
        from modules.telegram_alert import TelegramAlert
        print("✅ Telegram importado")
        
        from modules.ai_validator import AIValidator
        print("✅ IA importada")
        
        from modules.trading_logic import TradingLogic
        print("✅ Lógica de trading importada")
        
        from modules.logger import TradingLogger
        print("✅ Logger importado")
        
        from sheets_logger import SheetsLogger
        print("✅ Sheets Logger importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_config():
    """Verificar configuración"""
    print("\n⚙️ Verificando configuración...")
    
    try:
        from config_survivor_final import FinalSurvivorTradingConfig
        config = FinalSurvivorTradingConfig()
        
        # Verificar configuración
        config.validate_config()
        print("✅ Configuración válida")
        
        # Mostrar resumen
        print(config.get_target_summary())
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_bot_creation():
    """Verificar creación del bot"""
    print("\n🤖 Verificando creación del bot...")
    
    try:
        from main_survivor import SurvivorTradingBot
        bot = SurvivorTradingBot('breakout')
        print("✅ Bot creado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando bot: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 INICIO DE PRUEBAS DEL BOT")
    print("=" * 50)
    
    tests = [
        ("Variables de entorno", test_environment),
        ("Imports", test_imports),
        ("Configuración", test_config),
        ("Creación del bot", test_bot_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASÓ")
        else:
            print(f"❌ {test_name}: FALLÓ")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS PASARON - El bot está listo")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron - Revisar configuración")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
