#!/usr/bin/env python3
"""
🚀 PRODUCTION CONFIG - FAST-TRACK A REAL CON PARACAÍDAS
Configuración para transición segura a trading real con kill-switches
"""

import os
from datetime import datetime, time
from typing import Dict, Any

class ProductionConfig:
    """Configuración de producción con medidas de seguridad"""
    
    def __init__(self):
        # 1. FLAGS Y ENTORNO
        self.MODE = os.getenv('MODE', 'production')
        self.LIVE_TRADING = os.getenv('LIVE_TRADING', 'true').lower() == 'true'
        self.SHADOW_MODE = os.getenv('SHADOW_MODE', 'true').lower() == 'true'
        self.SYMBOL = os.getenv('SYMBOL', 'BNBUSDT')
        self.SESSION_WINDOW = os.getenv('SESSION_WINDOW', '09:00-22:00')
        self.TIMEZONE = os.getenv('TIMEZONE', 'Europe/Madrid')
        
        # 2. RIESGO
        self.POSITION_SIZING_MODE = os.getenv('POSITION_SIZING_MODE', 'percent_of_equity')
        self.POSITION_PERCENT = float(os.getenv('POSITION_PERCENT', '0.1'))  # 0.1%
        self.MIN_NOTIONAL_USD = float(os.getenv('MIN_NOTIONAL_USD', '5.0'))
        self.DAILY_MAX_DRAWDOWN_PCT = float(os.getenv('DAILY_MAX_DRAWDOWN_PCT', '0.5'))
        self.WEEKLY_MAX_DRAWDOWN_PCT = float(os.getenv('WEEKLY_MAX_DRAWDOWN_PCT', '1.5'))
        self.MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '2'))
        self.MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '8'))
        self.COOLDOWN_AFTER_LOSS_MIN = int(os.getenv('COOLDOWN_AFTER_LOSS_MIN', '30'))
        
        # 3. KILL-SWITCH Y REVERSIÓN
        self.KILL_SWITCH_TRIGGERED = False
        self.KILL_SWITCH_REASON = None
        self.AUTO_REVERT_TO_SHADOW = True
        
        # 4. TELEMETRÍA
        self.TELEMETRY_ENABLED = True
        self.SLIPPAGE_TRACKING = True
        self.FILL_LATENCY_TRACKING = True
        self.REAL_VS_TESTNET_COMPARISON = True
        
        # 5. VALIDACIONES
        self.MAX_LATENCY_MS = 1500
        self.MAX_RETRY_ATTEMPTS = 2
        self.PAUSE_AFTER_FAILURE_MIN = 15
        
        # 6. REPORTE FIN DE DÍA
        self.DAILY_REPORT_ENABLED = True
        self.READY_TO_SCALE_THRESHOLD_PF = 1.5
        self.READY_TO_SCALE_THRESHOLD_DD = 0.5
        self.READY_TO_SCALE = False
        
        # === FASE 1.6: MEJORAS DE RENTABILIDAD Y ROBUSTEZ ===
        
        # 7. FEES/SLIPPAGE
        self.FEE_TAKER_BPS = float(os.getenv('FEE_TAKER_BPS', '7.5'))  # 0.075%
        self.FEE_MAKER_BPS = float(os.getenv('FEE_MAKER_BPS', '2.0'))  # 0.02%
        self.SLIPPAGE_BPS = float(os.getenv('SLIPPAGE_BPS', '1.5'))  # 0.015%
        self.TP_BUFFER_BPS = float(os.getenv('TP_BUFFER_BPS', '2.0'))  # 0.02%
        
        # 8. OBJETIVOS DE SALIDA
        self.TP_MODE = os.getenv('TP_MODE', 'fixed_min')  # "fixed_min" | "atr_dynamic"
        self.TP_MIN_BPS = float(os.getenv('TP_MIN_BPS', '6.0'))  # 0.06%
        self.ATR_PERIOD = int(os.getenv('ATR_PERIOD', '14'))
        self.TP_ATR_MULT = float(os.getenv('TP_ATR_MULT', '0.50'))  # 0.5 * ATR%
        self.SL_ATR_MULT = float(os.getenv('SL_ATR_MULT', '0.40'))  # 0.4 * ATR%
        
        # 9. FILTROS DE ENTRADA
        self.MIN_RANGE_BPS = float(os.getenv('MIN_RANGE_BPS', '5.0'))  # 0.05%
        self.MAX_SPREAD_BPS = float(os.getenv('MAX_SPREAD_BPS', '2.0'))  # 0.02%
        self.MIN_VOL_USD = float(os.getenv('MIN_VOL_USD', '5000000'))  # 5M USD
        
        # 10. LATENCIA/ESTABILIDAD
        self.MAX_WS_LATENCY_MS = float(os.getenv('MAX_WS_LATENCY_MS', '1500'))
        self.MAX_REST_LATENCY_MS = float(os.getenv('MAX_REST_LATENCY_MS', '800'))
        self.RETRY_ORDER = int(os.getenv('RETRY_ORDER', '2'))
        
        # 11. BREAKEVEN (OPCIONAL)
        self.BREAKEVEN_ENABLED = os.getenv('BREAKEVEN_ENABLED', 'false').lower() == 'true'
        
        # Estado interno
        self.session_start_time = datetime.now()
        self.daily_trades_count = 0
        self.daily_pnl = 0.0
        self.daily_drawdown = 0.0
        self.consecutive_losses = 0
        self.last_trade_time = None
        
    def is_session_active(self) -> bool:
        """Verificar si estamos en horario de trading"""
        try:
            start_str, end_str = self.SESSION_WINDOW.split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            current_time = datetime.now().time()
            
            return start_time <= current_time <= end_time
        except:
            return True  # Si hay error, permitir trading
    
    def compute_trade_targets(self, price: float, atr_value: float = None) -> Dict[str, float]:
        """Calcular TP y SL dinámicos con fricción"""
        
        # Calcular fricción total
        fee_bps = max(self.FEE_TAKER_BPS, self.FEE_MAKER_BPS)
        fric_bps = 2 * fee_bps + self.SLIPPAGE_BPS  # entrada + salida + slippage
        tp_floor = fric_bps + self.TP_BUFFER_BPS
        
        if self.TP_MODE == "fixed_min":
            # Modo TP fijo mínimo
            tp_bps = max(self.TP_MIN_BPS, tp_floor)
            sl_bps = tp_bps / 1.25  # RR ≈ 1.25:1
        else:
            # Modo ATR dinámico
            if atr_value is None:
                atr_value = price * 0.01  # 1% por defecto
            
            atr_pct = (atr_value / price) * 100 * 100  # convertir a bps
            tp_bps = max(self.TP_ATR_MULT * atr_pct, tp_floor)
            sl_bps = max(self.SL_ATR_MULT * atr_pct, tp_floor / 1.25)
        
        return {
            'tp_bps': tp_bps,
            'sl_bps': sl_bps,
            'tp_floor': tp_floor,
            'fric_bps': fric_bps,
            'rr_ratio': tp_bps / sl_bps if sl_bps > 0 else 0,
            'tp_pct': tp_bps / 10000,  # convertir a porcentaje
            'sl_pct': sl_bps / 10000   # convertir a porcentaje
        }
    
    def check_kill_switches(self, current_capital: float, initial_capital: float = 50.0) -> Dict[str, Any]:
        """Verificar todos los kill-switches"""
        daily_drawdown = ((initial_capital - current_capital) / initial_capital) * 100
        
        kill_switches = {
            'triggered': False,
            'reason': None,
            'daily_drawdown': daily_drawdown,
            'consecutive_losses': self.consecutive_losses,
            'daily_trades': self.daily_trades_count
        }
        
        # Kill-switches
        if daily_drawdown >= self.DAILY_MAX_DRAWDOWN_PCT:
            kill_switches['triggered'] = True
            kill_switches['reason'] = f"Daily drawdown limit exceeded: {daily_drawdown:.2f}%"
            
        elif self.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
            kill_switches['triggered'] = True
            kill_switches['reason'] = f"Max consecutive losses reached: {self.consecutive_losses}"
            
        elif self.daily_trades_count >= self.MAX_TRADES_PER_DAY:
            kill_switches['triggered'] = True
            kill_switches['reason'] = f"Max daily trades reached: {self.daily_trades_count}"
        
        return kill_switches
    
    def trigger_kill_switch(self, reason: str):
        """Activar kill-switch y revertir a shadow mode"""
        self.KILL_SWITCH_TRIGGERED = True
        self.KILL_SWITCH_REASON = reason
        self.LIVE_TRADING = False
        self.SHADOW_MODE = True
        
        return {
            'live_trading': False,
            'shadow_mode': True,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_ready_to_scale(self, daily_pf: float, daily_dd: float) -> bool:
        """Verificar si está listo para escalar"""
        if daily_pf >= self.READY_TO_SCALE_THRESHOLD_PF and daily_dd <= self.READY_TO_SCALE_THRESHOLD_DD:
            self.READY_TO_SCALE = True
            return True
        return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtener resumen de configuración"""
        return {
            'mode': self.MODE,
            'live_trading': self.LIVE_TRADING,
            'shadow_mode': self.SHADOW_MODE,
            'symbol': self.SYMBOL,
            'session_window': self.SESSION_WINDOW,
            'position_percent': self.POSITION_PERCENT,
            'daily_max_drawdown': self.DAILY_MAX_DRAWDOWN_PCT,
            'max_consecutive_losses': self.MAX_CONSECUTIVE_LOSSES,
            'max_trades_per_day': self.MAX_TRADES_PER_DAY,
            'kill_switch_triggered': self.KILL_SWITCH_TRIGGERED,
            'ready_to_scale': self.READY_TO_SCALE,
            # FASE 1.6
            'tp_mode': self.TP_MODE,
            'tp_min_bps': self.TP_MIN_BPS,
            'fee_taker_bps': self.FEE_TAKER_BPS,
            'slippage_bps': self.SLIPPAGE_BPS,
            'min_range_bps': self.MIN_RANGE_BPS,
            'max_spread_bps': self.MAX_SPREAD_BPS,
            'min_vol_usd': self.MIN_VOL_USD
        }

# Instancia global
production_config = ProductionConfig()
