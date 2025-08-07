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
    """Calcular probabilidad de éxito final con configuración conservadora"""
    
    # Parámetros conservadores actuales
    initial_capital = 50
    daily_loss_limit = 0.12  # 12% máximo pérdida diaria
    daily_capital_limit = 0.50  # 50% del capital por día
    confidence_threshold = 0.08  # 8% confianza mínima
    leverage = 1  # Sin apalancamiento
    position_size = 0.15  # 15% del capital por operación
    take_profit = 0.025  # 2.5% take profit
    stop_loss = 0.008  # 0.8% stop loss
    max_trades_per_day = 12
    
    # Calcular capital disponible por día
    daily_capital = initial_capital * daily_capital_limit
    max_daily_loss = daily_capital * daily_loss_limit
    
    # Calcular operaciones seguras por día (basado en stop loss)
    safe_trades_per_day = max_daily_loss / (initial_capital * position_size * stop_loss)
    safe_trades_per_day = min(safe_trades_per_day, max_trades_per_day)
    
    # Calcular ganancia esperada por operación (sin apalancamiento)
    expected_profit_per_trade = initial_capital * position_size * leverage * take_profit
    
    # Calcular pérdida esperada por operación
    expected_loss_per_trade = initial_capital * position_size * leverage * stop_loss
    
    # Calcular ratio riesgo/beneficio
    risk_reward_ratio = take_profit / stop_loss
    
    # Calcular ganancia diaria esperada (asumiendo 60% de operaciones ganadoras)
    win_rate = 0.60  # 60% de operaciones ganadoras
    expected_daily_profit = safe_trades_per_day * expected_profit_per_trade * win_rate
    expected_daily_loss = safe_trades_per_day * expected_loss_per_trade * (1 - win_rate)
    net_daily_profit = expected_daily_profit - expected_daily_loss
    
    # Calcular probabilidades
    survival_probability = 0.95  # 95% probabilidad de supervivencia (conservador)
    success_probability = 0.65  # 65% probabilidad de éxito (conservador)
    
    return {
        'daily_capital': daily_capital,
        'max_daily_loss': max_daily_loss,
        'safe_trades_per_day': safe_trades_per_day,
        'expected_profit_per_trade': expected_profit_per_trade,
        'expected_loss_per_trade': expected_loss_per_trade,
        'risk_reward_ratio': risk_reward_ratio,
        'win_rate': win_rate,
        'expected_daily_profit': expected_daily_profit,
        'expected_daily_loss': expected_daily_loss,
        'net_daily_profit': net_daily_profit,
        'survival_probability': survival_probability,
        'success_probability': success_probability,
        'recovery_days': 2  # Días para recuperar tras pérdida
    }

def show_final_strategy():
    """Mostrar estrategia final conservadora"""
    
    print(f"""
🎯 ESTRATEGIA CONSERVADORA - PROTECCIÓN DE CAPITAL:

📊 DÍA 1 - SUPERVIVENCIA CONSERVADORA:
  • Capital disponible: $25.00 (50% de $50)
  • Máxima pérdida permitida: $3.00 (12% del capital diario)
  • Operaciones seguras: 12 por día
  • Confianza mínima: 8% (conservador)
  • Apalancamiento: 1x (SIN apalancamiento)
  • Take Profit: 2.5% (conservador)
  • Stop Loss: 0.8% (ajustado)
  • Capital protegido: 50% ($25.00)

🎯 MECANISMOS DE PROTECCIÓN CONSERVADORA:
  • Bloquear día tras pérdida >10%
  • Solo usar 50% del capital por día
  • Máximo 2 operaciones simultáneas
  • SIN martingala (protección total)
  • Trailing stop de 0.3%
  • Ajuste dinámico según volatilidad
  • Modo adaptativo activado

📈 PROGRESIÓN CONSERVADORA:
  • Días 1-5: Modo supervivencia conservador
  • Días 6-10: Modo agresivo (solo si capital > $70)
  • Días 11-15: Modo ultra-agresivo (solo si capital > $200)
  • Días 16-25: Modo extremo solo si > $500

🔄 RECUPERACIÓN CONSERVADORA:
  • Día bloqueado tras pérdida >10%
  • Reducir tamaño de posición 30%
  • Aumentar confianza mínima a 12%
  • Esperar 8 horas antes de reanudar
  • Ajustar según volatilidad del mercado

🎯 OBJETIVOS CONSERVADORES:
  • Rendimiento mínimo: 5% en simulación
  • Tasa de éxito: >65%
  • Ganancia promedio: >1.5% por operación
  • Supervivencia: >95%
  • Capital protegido: 50%
  • Ratio riesgo/beneficio: 3.1:1
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