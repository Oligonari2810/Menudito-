"""
⚙️ CONFIGURACIÓN CENTRALIZADA - Bot de Trading Mejorado
Configuración para todas las funcionalidades del bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    """Configuración centralizada del bot de trading"""
    
    # ===== CONFIGURACIÓN DE BROKERS =====
    BINANCE = {
        'api_key': os.getenv('BINANCE_API_KEY'),
        'secret_key': os.getenv('BINANCE_SECRET_KEY'),
        'testnet': True,  # Siempre testnet por seguridad
        'symbol': 'BTCUSDT',
        'base_currency': 'USDT'
    }
    
    # ===== CONFIGURACIÓN DE TRADING =====
    TRADING = {
        'initial_capital': float(os.getenv('INITIAL_CAPITAL', 100)),
        'confidence_threshold': 0.15,  # 15% mínimo para ejecutar (menos restrictivo para testnet)
        'stop_loss_percent': float(os.getenv('STOP_LOSS_PERCENT', 2.0)),
        'take_profit_percent': float(os.getenv('TAKE_PROFIT_PERCENT', 3.0)),
        'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS', 5.0)),
        'position_size_percent': 0.02,  # 2% del capital por operación
        'update_interval': 300  # 5 minutos
    }
    
    # ===== CONFIGURACIÓN DE ESTRATEGIAS =====
    STRATEGIES = {
        'breakout': {
            'name': 'Breakout Diario',
            'lookback_period': 20,
            'breakout_threshold': 0.02,
            'enabled': True
        },
        'scalping': {
            'name': 'Scalping Simple',
            'buy_threshold': 0.01,
            'sell_threshold': 0.015,
            'max_hold_time': 30,
            'enabled': True
        }
    }
    
    # ===== CONFIGURACIÓN DE NOTIFICACIONES =====
    TELEGRAM = {
        'enabled': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'notify_signals': True,
        'notify_trades': True,
        'notify_reports': True
    }
    
    # ===== CONFIGURACIÓN DE IA =====
    OPENAI = {
        'enabled': True,  # Habilitado con plan de pago
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',
        'max_tokens': 150,
        'temperature': 0.3
    }
    
    # ===== CONFIGURACIÓN DE LOGGING =====
    LOGGING = {
        'level': 'INFO',
        'file_path': 'logs/trading_enhanced.log',
        'backup_count': 5,
        'max_bytes': 10 * 1024 * 1024  # 10MB
    }
    
    # ===== CONFIGURACIÓN DEL SISTEMA =====
    SYSTEM = {
        'timezone': 'America/Santo_Domingo',
        'debug_mode': False,
        'paper_trading': True,  # Siempre paper trading por defecto
        'max_retries': 3,
        'timeout': 30
    }
    
    @classmethod
    def validate_config(cls):
        """Validar configuración del sistema"""
        errors = []
        
        # Verificar Binance
        if not cls.BINANCE['api_key'] or cls.BINANCE['api_key'] == 'tu_api_key_aqui':
            errors.append("❌ API Key de Binance no configurada")
        
        if not cls.BINANCE['secret_key'] or cls.BINANCE['secret_key'] == 'tu_secret_key_aqui':
            errors.append("❌ Secret Key de Binance no configurada")
        
        # Verificar Telegram (opcional)
        if not cls.TELEGRAM['enabled']:
            print("⚠️ Telegram no configurado (opcional)")
        
        # Verificar OpenAI (opcional)
        if not cls.OPENAI['enabled']:
            print("⚠️ OpenAI no configurado (opcional)")
        
        return errors
    
    @classmethod
    def get_config_summary(cls):
        """Obtener resumen de configuración"""
        errors = cls.validate_config()
        
        summary = f"""
🤖 CONFIGURACIÓN DEL BOT MEJORADO
{'='*50}

💰 CAPITAL INICIAL: ${cls.TRADING['initial_capital']}
📊 SÍMBOLO: {cls.BINANCE['symbol']}
🎯 UMBRAL DE CONFIANZA: {cls.TRADING['confidence_threshold']*100}%
🛑 STOP LOSS: {cls.TRADING['stop_loss_percent']}%
🎯 TAKE PROFIT: {cls.TRADING['take_profit_percent']}%

📱 NOTIFICACIONES:
  • Telegram: {'✅' if cls.TELEGRAM['enabled'] else '❌'}
  • OpenAI: {'✅' if cls.OPENAI['enabled'] else '❌'}

📊 LOGGING:
  • Archivo: {cls.LOGGING['file_path']}

🔧 VALIDACIÓN:
"""
        
        if errors:
            for error in errors:
                summary += f"  {error}\n"
        else:
            summary += "  ✅ Configuración válida\n"
        
        return summary 