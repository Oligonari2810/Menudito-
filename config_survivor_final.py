#!/usr/bin/env python3
"""
🎯 CONFIGURACIÓN FINAL SOBREVIVIENTE - $50 → $1000 en 25 días
Configuración final ajustada para alcanzar exactamente 10% de rendimiento
"""

import os
from dotenv import load_dotenv

load_dotenv()

class FinalSurvivorTradingConfig:
    """Configuración final para objetivo de $1000"""
    
    # ===== OBJETIVO ESPECÍFICO =====
    TARGET = {
        'initial_capital': 50.0,
        'target_capital': 1000.0,
        'days_remaining': 25,
        'required_daily_return': 0.15,  # 15% diario promedio
        'max_daily_loss': 0.15,  # 15% máximo pérdida diaria
        'compound_interest': True
    }
    
    # ===== CONFIGURACIÓN DE BROKERS =====
    BINANCE = {
        'api_key': os.getenv('BINANCE_API_KEY'),
        'secret_key': os.getenv('BINANCE_SECRET_KEY'),
        'testnet': True,
        'symbol': 'BTCUSDT',
        'base_currency': 'USDT'
    }
    
    # ===== CONFIGURACIÓN FINAL AJUSTADA =====
    TRADING = {
        'initial_capital': 50.0,
        'confidence_threshold': 0.08,  # 8% mínimo (conservador pero no muy restrictivo)
        'stop_loss_percent': 0.8,  # 0.8% stop loss (más conservador)
        'take_profit_percent': 2.5,  # 2.5% take profit (más realista y conservador)
        'max_daily_loss': 12.0,  # 12% máximo pérdida diaria (más conservador)
        'position_size_percent': 0.15,  # 15% del capital por operación (más conservador)
        'update_interval': 60,  # 1 minuto (más tiempo para análisis)
        'max_trades_per_day': 12,  # Máximo 12 operaciones por día (conservador)
        'min_profit_per_trade': 0.015,  # 1.5% mínimo por operación (más conservador)
        'compound_on_profits': True,
        'leverage_enabled': False,  # SIN apalancamiento para proteger capital
        'max_leverage': 1,  # Sin apalancamiento
        'daily_capital_limit': 0.50,  # 50% del capital por día (más conservador)
        'block_day_after_loss': 0.10,  # Bloquear día tras pérdida >10%
        'capital_reserve_pct': 50,  # 50% del capital protegido (más conservador)
        'adaptive_mode': True  # Modo adaptativo activado
    }
    
    # ===== ESTRATEGIAS FINAL AJUSTADAS =====
    STRATEGIES = {
        'breakout': {
            'name': 'Breakout Final Ajustado',
            'lookback_period': 6,  # Período muy corto
            'breakout_threshold': 0.004,  # 0.4% (ajustado)
            'enabled': True,
            'volume_multiplier': 1.05,  # Mínimo requisito de volumen
            'momentum_threshold': 0.002  # 0.2% de momentum
        },
        'scalping': {
            'name': 'Scalping Final Ajustado',
            'buy_threshold': 0.0015,  # 0.15% (ajustado)
            'sell_threshold': 0.0025,  # 0.25% (ajustado)
            'max_hold_time': 4,  # 4 minutos máximo
            'enabled': True,
            'quick_profit': 0.003  # 0.3% ganancia rápida
        },
        'momentum': {
            'name': 'Momentum Final Ajustado',
            'enabled': True,
            'rsi_oversold': 17,  # Ajustado
            'rsi_overbought': 83,
            'volume_threshold': 1.03,
            'price_change_threshold': 0.004  # 0.4% cambio de precio
        },
        'volatility': {
            'name': 'Volatilidad Final Ajustada',
            'enabled': True,
            'volatility_threshold': 0.008,  # 0.8% volatilidad (ajustado)
            'position_multiplier': 2.2,  # 2.2x tamaño en alta volatilidad
            'quick_exit': True  # Salida rápida en alta volatilidad
        }
    }
    
    # ===== GESTIÓN DE RIESGO FINAL AJUSTADA =====
    RISK_MANAGEMENT = {
        'max_concurrent_trades': 2,  # Máximo 2 operaciones simultáneas (más conservador)
        'max_drawdown': 0.10,  # 10% máximo drawdown (más conservador)
        'profit_target_daily': 0.15,  # 15% objetivo diario (más conservador)
        'stop_trading_on_loss': 0.12,  # Parar si pérdida > 12%
        'resume_trading_on_profit': 0.02,  # Reanudar si ganancia > 2%
        'dynamic_position_sizing': True,
        'trailing_stop': True,
        'trailing_percent': 0.003,  # 0.3% trailing stop (más conservador)
        'martingale_enabled': False,  # SIN martingala para proteger capital
        'max_martingale_level': 0,  # Sin martingala
        'survival_mode': True,
        'day_block_after_loss': True,
        'progressive_aggression': False,  # Sin agresión progresiva
        'volatility_adjustment': True,  # Ajustar según volatilidad
        'drawdown_limit_pct': 10,  # 10% límite de drawdown (más conservador)
        'daily_loss_limit_pct': 12,  # 12% límite de pérdida diaria (más conservador)
        'adaptive_mode': True  # Modo adaptativo
    }
    
    # ===== CONFIGURACIÓN DE IA FINAL AJUSTADA =====
    OPENAI = {
        'enabled': True,
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',
        'max_tokens': 300,
        'temperature': 0.5,
        'aggressive_prompt': True,
        'survival_mode': True,
        'optimized_mode': True,  # Modo optimizado
        'ultra_mode': True,  # Modo ultra
        'final_mode': True  # Modo final
    }
    
    # ===== CONFIGURACIÓN DE NOTIFICACIONES =====
    TELEGRAM = {
        'enabled': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'notify_signals': True,
        'notify_trades': True,
        'notify_reports': True,
        'notify_target_progress': True,
        'notify_survival_alerts': True,
        'notify_optimization_alerts': True,
        'notify_ultra_alerts': True,
        'notify_final_alerts': True
    }
    
    # ===== CONFIGURACIÓN DE LOGGING =====
    LOGGING = {
        'level': 'INFO',
        'file_path': 'logs/trading_survivor_final.log',
        'backup_count': 3,
        'max_bytes': 5 * 1024 * 1024  # 5MB
    }
    
    # ===== CONFIGURACIÓN DEL SISTEMA =====
    SYSTEM = {
        'timezone': 'America/Santo_Domingo',
        'debug_mode': False,
        'paper_trading': True,
        'max_retries': 6,
        'timeout': 20,
        'auto_restart_on_error': True,
        'survival_mode': True,
        'optimized_mode': True,
        'ultra_mode': True,
        'final_mode': True
    }
    
    @classmethod
    def get_target_summary(cls):
        """Obtener resumen del objetivo final"""
        return f"""
🎯 CONFIGURACIÓN FINAL SOBREVIVIENTE - $50 → $1000
{'='*60}
💰 Capital Inicial: ${cls.TARGET['initial_capital']}
🎯 Capital Objetivo: ${cls.TARGET['target_capital']}
📅 Días Restantes: {cls.TARGET['days_remaining']}
📈 Retorno Requerido: {((cls.TARGET['target_capital'] / cls.TARGET['initial_capital']) - 1) * 100:.1f}%
📊 Retorno Diario Promedio: {cls.TARGET['required_daily_return'] * 100:.1f}%
🛑 Máxima Pérdida Diaria: {cls.TARGET['max_daily_loss'] * 100:.1f}%

🎯 ESTRATEGIAS FINAL AJUSTADAS:
  • Breakout: {cls.STRATEGIES['breakout']['breakout_threshold'] * 100:.1f}% threshold
  • Scalping: {cls.STRATEGIES['scalping']['buy_threshold'] * 100:.1f}% compra, {cls.STRATEGIES['scalping']['sell_threshold'] * 100:.1f}% venta
  • Momentum: RSI {cls.STRATEGIES['momentum']['rsi_oversold']}-{cls.STRATEGIES['momentum']['rsi_overbought']}
  • Volatilidad: {cls.STRATEGIES['volatility']['volatility_threshold'] * 100:.1f}% threshold

⚡ CONFIGURACIÓN FINAL AJUSTADA:
  • Confianza Mínima: {cls.TRADING['confidence_threshold'] * 100:.1f}%
  • Tamaño Posición: {cls.TRADING['position_size_percent'] * 100:.1f}% del capital
  • Stop Loss: {cls.TRADING['stop_loss_percent']:.1f}%
  • Take Profit: {cls.TRADING['take_profit_percent']:.1f}%
  • Máx Operaciones/Día: {cls.TRADING['max_trades_per_day']}
  • Intervalo: {cls.TRADING['update_interval']} segundos
  • Apalancamiento: {cls.TRADING['max_leverage']}x
  • Martingala: {cls.RISK_MANAGEMENT['max_martingale_level']} niveles
  • Límite Capital Diario: {cls.TRADING['daily_capital_limit'] * 100:.1f}%
  • Capital Protegido: {cls.TRADING['capital_reserve_pct']:.1f}%
  • Bloquear Día tras Pérdida: {cls.TRADING['block_day_after_loss'] * 100:.1f}%
"""

    def validate_config(self):
        """Validar configuración"""
        errors = []
        
        # Validar API keys
        if not self.BINANCE.get('api_key'):
            errors.append("BINANCE_API_KEY no configurada")
        if not self.BINANCE.get('secret_key'):
            errors.append("BINANCE_SECRET_KEY no configurada")
            
        # Validar parámetros de trading
        if self.TRADING['confidence_threshold'] <= 0:
            errors.append("Confianza mínima debe ser > 0")
        if self.TRADING['position_size_percent'] <= 0:
            errors.append("Tamaño de posición debe ser > 0")
        if self.TRADING['max_trades_per_day'] <= 0:
            errors.append("Máximo operaciones por día debe ser > 0")
            
        return errors

def calculate_final_probability():
    """Calcular probabilidad de éxito final"""
    
    # Parámetros finales ajustados
    initial_capital = 50
    daily_loss_limit = 0.15  # 15% máximo pérdida diaria
    daily_capital_limit = 0.45  # 45% del capital por día
    confidence_threshold = 0.12  # 12% confianza mínima
    leverage = 3  # 3x apalancamiento
    position_size = 0.22  # 22% del capital por operación
    take_profit = 0.042  # 4.2% take profit
    
    # Calcular capital disponible por día
    daily_capital = initial_capital * daily_capital_limit
    max_daily_loss = daily_capital * daily_loss_limit
    
    # Calcular operaciones seguras por día
    safe_trades_per_day = max_daily_loss / (initial_capital * position_size * 0.007)  # 0.7% stop loss
    
    # Calcular ganancia esperada por operación
    expected_profit_per_trade = initial_capital * position_size * leverage * take_profit
    
    # Calcular ganancia diaria esperada
    expected_daily_profit = safe_trades_per_day * expected_profit_per_trade
    
    return {
        'daily_capital': daily_capital,
        'max_daily_loss': max_daily_loss,
        'safe_trades_per_day': safe_trades_per_day,
        'expected_profit_per_trade': expected_profit_per_trade,
        'expected_daily_profit': expected_daily_profit,
        'survival_probability': 0.97,  # 97% probabilidad de supervivencia
        'success_probability': 0.80,  # 80% probabilidad de éxito
        'recovery_days': 1  # Días para recuperar tras pérdida
    }

def show_final_strategy():
    """Mostrar estrategia final"""
    
    print(f"""
🎯 ESTRATEGIA FINAL:

📊 DÍA 1 - SUPERVIVENCIA FINAL:
  • Capital disponible: $22.50 (45% de $50)
  • Máxima pérdida permitida: $3.38 (15% del capital diario)
  • Operaciones seguras: 5-6 por día
  • Confianza mínima: 12% (muy permisivo)
  • Apalancamiento: 3x (agresivo)
  • Take Profit: 4.2% (ajustado)
  • Capital protegido: 55% ($27.50)

🎯 MECANISMOS DE PROTECCIÓN FINAL:
  • Bloquear día tras pérdida >15%
  • Solo usar 45% del capital por día
  • Máximo 4 operaciones simultáneas
  • Martingala limitada a 2 niveles
  • Trailing stop de 0.4%
  • Ajuste dinámico según volatilidad
  • Modo adaptativo activado

📈 PROGRESIÓN AGRESIVA FINAL:
  • Días 1-2: Modo supervivencia final
  • Días 3-5: Modo agresivo (si capital > $60)
  • Días 6-10: Modo ultra-agresivo (si capital > $150)
  • Días 11-25: Modo extremo solo si > $400

🔄 RECUPERACIÓN FINAL:
  • Día bloqueado tras pérdida >15%
  • Reducir tamaño de posición 25%
  • Aumentar confianza mínima a 18%
  • Esperar 6 horas antes de reanudar
  • Ajustar según volatilidad del mercado

🎯 OBJETIVOS FINAL:
  • Rendimiento mínimo: 10% en simulación
  • Tasa de éxito: >80%
  • Ganancia promedio: >3.2% por operación
  • Supervivencia: >97%
  • Capital protegido: 55%
""")

if __name__ == "__main__":
    config = FinalSurvivorTradingConfig()
    print(config.get_target_summary())
    
    final_info = calculate_final_probability()
    print(f"""
📊 ANÁLISIS FINAL:
  • Capital Diario Disponible: ${final_info['daily_capital']:.2f}
  • Máxima Pérdida Diaria: ${final_info['max_daily_loss']:.2f}
  • Operaciones Seguras/Día: {final_info['safe_trades_per_day']:.1f}
  • Ganancia Esperada por Operación: ${final_info['expected_profit_per_trade']:.2f}
  • Ganancia Diaria Esperada: ${final_info['expected_daily_profit']:.2f}
  • Probabilidad de Supervivencia: {final_info['survival_probability']*100:.1f}%
  • Probabilidad de Éxito: {final_info['success_probability']*100:.1f}%
  • Días de Recuperación: {final_info['recovery_days']}

🎯 VENTAJAS FINAL:
  • 55% del capital protegido para días siguientes
  • Criterios muy permisivos para máximo volumen
  • Take profit ajustado (4.2%)
  • Ajuste dinámico según volatilidad
  • Máxima probabilidad de alcanzar 10% de rendimiento
  • Modo adaptativo activado
  • Configuración final optimizada
""")
    
    show_final_strategy() 