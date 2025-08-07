#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA
Revisión desde cero de toda la configuración
"""

import os
import sys
import logging
import json
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Verificar todas las variables de entorno"""
    logger.info("🔍 VERIFICANDO VARIABLES DE ENTORNO")
    logger.info("=" * 50)
    
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY', 
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'OPENAI_API_KEY',
        'GOOGLE_SHEETS_CREDENTIALS'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: Configurado")
        else:
            logger.warning(f"❌ {var}: FALTANTE")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Variables faltantes: {missing_vars}")
        return False
    
    logger.info("✅ Todas las variables de entorno configuradas")
    return True

def check_dependencies():
    """Verificar todas las dependencias"""
    logger.info("\n📦 VERIFICANDO DEPENDENCIAS")
    logger.info("=" * 50)
    
    dependencies = [
        'requests',
        'gspread',
        'google-auth',
        'google-auth-oauthlib',
        'schedule',
        'flask'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"✅ {dep}: Instalado")
        except ImportError:
            logger.error(f"❌ {dep}: NO instalado")
            missing_deps.append(dep)
    
    if missing_deps:
        logger.error(f"❌ Dependencias faltantes: {missing_deps}")
        return False
    
    logger.info("✅ Todas las dependencias instaladas")
    return True

def check_google_sheets():
    """Verificar Google Sheets"""
    logger.info("\n📊 VERIFICANDO GOOGLE SHEETS")
    logger.info("=" * 50)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_env = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_env:
            logger.error("❌ GOOGLE_SHEETS_CREDENTIALS no encontrada")
            return False
        
        # Parsear credenciales
        creds_dict = json.loads(credentials_env)
        logger.info("✅ Credenciales JSON válidas")
        
        # Configurar cliente
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        logger.info("✅ Cliente autorizado")
        
        # Abrir spreadsheet
        spreadsheet = client.open_by_key("1aks2jTMCacJ5rdigtolhHB3JiSw5B8rWDHYT_rjk69U")
        logger.info(f"✅ Spreadsheet: {spreadsheet.title}")
        
        # Obtener worksheet
        worksheet = spreadsheet.worksheet("Trading Log")
        logger.info("✅ Worksheet 'Trading Log' encontrado")
        
        # Test de escritura
        test_data = [
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%H:%M:%S"),
            "BTCUSDT",
            "BUY",
            "$114,909.34",
            "0.000087",
            "$10.00",
            "breakout",
            "0.6%",
            "DIAGNÓSTICO COMPLETO",
            "COMPLETED",
            "$0.00",
            "$49.29"
        ]
        
        worksheet.append_row(test_data)
        logger.info("✅ Escritura exitosa")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error Google Sheets: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

def check_telegram():
    """Verificar Telegram"""
    logger.info("\n📱 VERIFICANDO TELEGRAM")
    logger.info("=" * 50)
    
    try:
        import requests
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.error("❌ Token o Chat ID faltantes")
            return False
        
        # Test de conexión
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            logger.info(f"✅ Bot: {bot_info['result']['username']}")
            
            # Test de envío
            send_url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': '🔍 DIAGNÓSTICO COMPLETO\n\n✅ Telegram funcionando\n📊 Sistema verificado',
                'parse_mode': 'HTML'
            }
            
            send_response = requests.post(send_url, json=data, timeout=10)
            if send_response.status_code == 200:
                logger.info("✅ Mensaje enviado exitosamente")
                return True
            else:
                logger.error(f"❌ Error enviando mensaje: {send_response.status_code}")
                return False
        else:
            logger.error(f"❌ Error verificando bot: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error Telegram: {e}")
        return False

def check_bot_code():
    """Verificar código del bot"""
    logger.info("\n🤖 VERIFICANDO CÓDIGO DEL BOT")
    logger.info("=" * 50)
    
    try:
        # Importar el bot
        from minimal_working_bot import ProfessionalTradingBot
        
        # Crear instancia
        bot = ProfessionalTradingBot()
        logger.info("✅ Bot creado exitosamente")
        
        # Verificar componentes
        if hasattr(bot, 'sheets_logger'):
            logger.info("✅ Google Sheets Logger configurado")
        else:
            logger.warning("⚠️ Google Sheets Logger no encontrado")
        
        if hasattr(bot, 'symbol'):
            logger.info(f"✅ Símbolo configurado: {bot.symbol}")
        else:
            logger.warning("⚠️ Símbolo no configurado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando código del bot: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    logger.info("=" * 60)
    
    results = {}
    
    # Verificar entorno
    results['environment'] = check_environment()
    
    # Verificar dependencias
    results['dependencies'] = check_dependencies()
    
    # Verificar Google Sheets
    results['google_sheets'] = check_google_sheets()
    
    # Verificar Telegram
    results['telegram'] = check_telegram()
    
    # Verificar código del bot
    results['bot_code'] = check_bot_code()
    
    # Resumen
    logger.info("\n📊 RESUMEN DEL DIAGNÓSTICO")
    logger.info("=" * 60)
    
    all_passed = True
    for component, status in results.items():
        if status:
            logger.info(f"✅ {component.upper()}: OK")
        else:
            logger.error(f"❌ {component.upper()}: FALLA")
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 DIAGNÓSTICO EXITOSO")
        logger.info("✅ Todos los componentes funcionando")
        logger.info("🚀 El bot está listo para funcionar")
    else:
        logger.error("\n❌ DIAGNÓSTICO FALLIDO")
        logger.error("🔧 Revisar componentes con fallas")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
