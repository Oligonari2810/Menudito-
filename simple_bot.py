#!/usr/bin/env python3
"""
🤖 Bot Simplificado para Diagnóstico
Versión mínima para identificar problemas
"""

import os
import sys
import time
import logging
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_environment():
    """Probar variables de entorno"""
    print("🔍 Probando variables de entorno...")
    
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'OPENAI_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configurado")
        else:
            print(f"❌ {var}: FALTANTE")
            return False
    
    return True

def test_imports():
    """Probar imports básicos"""
    print("\n📦 Probando imports...")
    
    try:
        import requests
        print("✅ requests: OK")
        
        import schedule
        print("✅ schedule: OK")
        
        import gspread
        print("✅ gspread: OK")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Probar configuración"""
    print("\n⚙️ Probando configuración...")
    
    try:
        from config_survivor_final import FinalSurvivorTradingConfig
        config = FinalSurvivorTradingConfig()
        print("✅ Configuración cargada")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def simple_bot_loop():
    """Bucle simple del bot"""
    print("\n🤖 Iniciando bucle simple del bot...")
    
    counter = 0
    while True:
        try:
            counter += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Bot ejecutándose... (iteración {counter})")
            
            # Simular trabajo del bot
            time.sleep(30)  # Esperar 30 segundos
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por usuario")
            break
        except Exception as e:
            print(f"❌ Error en bucle: {e}")
            time.sleep(10)

def main():
    """Función principal"""
    print("🧪 BOT SIMPLIFICADO PARA DIAGNÓSTICO")
    print("=" * 50)
    
    # Probar componentes básicos
    if not test_environment():
        print("❌ Variables de entorno faltantes")
        return False
    
    if not test_imports():
        print("❌ Imports fallaron")
        return False
    
    if not test_config():
        print("❌ Configuración falló")
        return False
    
    print("✅ Todas las pruebas pasaron")
    print("🚀 Iniciando bot simplificado...")
    
    # Iniciar bucle simple
    simple_bot_loop()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
