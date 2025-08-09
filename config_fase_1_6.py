#!/usr/bin/env python3
"""
⚙️ CONFIGURACIÓN FASE 1.6
Archivo de configuración centralizada para todas las variables de FASE 1.6
"""

import os
from typing import Dict, Any, List, Optional

class Fase16Config:
    """Configuración centralizada FASE 1.6"""
    
    def __init__(self):
        # === FASE 1.6: FLAGS Y ENTORNO ===
        self.MODE = os.getenv('MODE', 'production')
        self.LIVE_TRADING = os.getenv('LIVE_TRADING', 'true').lower() == 'true'
        self.SHADOW_MODE = os.getenv('SHADOW_MODE', 'true').lower() == 'true'
        self.SYMBOL = os.getenv('SYMBOL', 'BNBUSDT')
        self.SESSION_WINDOW = os.getenv('SESSION_WINDOW', '09:00-22:00 Europe/Madrid')
        self.TIMEZONE = os.getenv('TIMEZONE', 'Europe/Madrid')
        
        # === FASE 1.6: RIESGO ===
        self.POSITION_SIZING_MODE = os.getenv('POSITION_SIZING_MODE', 'percent_of_equity')
        self.POSITION_PERCENT = float(os.getenv('POSITION_PERCENT', '0.10'))
        self.MIN_NOTIONAL_USD = float(os.getenv('MIN_NOTIONAL_USD', '5'))
        self.DAILY_MAX_DRAWDOWN_PCT = float(os.getenv('DAILY_MAX_DRAWDOWN_PCT', '0.50'))
        self.WEEKLY_MAX_DRAWDOWN_PCT = float(os.getenv('WEEKLY_MAX_DRAWDOWN_PCT', '1.50'))
        self.MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '2'))
        self.MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '8'))
        self.COOLDOWN_AFTER_LOSS_MIN = int(os.getenv('COOLDOWN_AFTER_LOSS_MIN', '30'))
        
        # === FASE 1.6: FEES/SLIPPAGE ===
        self.FEE_TAKER_BPS = float(os.getenv('FEE_TAKER_BPS', '7.5'))
        self.FEE_MAKER_BPS = float(os.getenv('FEE_MAKER_BPS', '2.0'))
        self.SLIPPAGE_BPS = float(os.getenv('SLIPPAGE_BPS', '1.5'))
        self.TP_BUFFER_BPS = float(os.getenv('TP_BUFFER_BPS', '2.0'))
        
        # === FASE 1.6: OBJETIVOS DE SALIDA ===
        self.TP_MODE = os.getenv('TP_MODE', 'fixed_min')
        self.TP_MIN_BPS = float(os.getenv('TP_MIN_BPS', '18.5'))
        self.ATR_PERIOD = int(os.getenv('ATR_PERIOD', '14'))
        self.TP_ATR_MULT = float(os.getenv('TP_ATR_MULT', '0.50'))
        self.SL_ATR_MULT = float(os.getenv('SL_ATR_MULT', '0.40'))
        
        # === FASE 1.6: FILTROS DE ENTRADA ===
        self.MIN_RANGE_BPS = float(os.getenv('MIN_RANGE_BPS', '5.0'))
        self.MAX_SPREAD_BPS = float(os.getenv('MAX_SPREAD_BPS', '2.0'))
        self.MIN_VOL_USD = float(os.getenv('MIN_VOL_USD', '5000000'))
        
        # === FASE 1.6: LATENCIA/ESTABILIDAD ===
        self.MAX_WS_LATENCY_MS = float(os.getenv('MAX_WS_LATENCY_MS', '1500'))
        self.MAX_REST_LATENCY_MS = float(os.getenv('MAX_REST_LATENCY_MS', '800'))
        self.RETRY_ORDER = int(os.getenv('RETRY_ORDER', '2'))
        
        # === FASE 1.6: KILL-SWITCH ===
        self.KILL_SWITCH_TRIGGERED = os.getenv('KILL_SWITCH_TRIGGERED', 'false').lower() == 'true'
        self.KILL_SWITCH_REASON = os.getenv('KILL_SWITCH_REASON', '')
        self.AUTO_REVERT_TO_SHADOW = os.getenv('AUTO_REVERT_TO_SHADOW', 'true').lower() == 'true'
        
        # === FASE 1.6: TELEMETRÍA ===
        self.TELEMETRY_ENABLED = os.getenv('TELEMETRY_ENABLED', 'true').lower() == 'true'
        self.SLIPPAGE_TRACKING = os.getenv('SLIPPAGE_TRACKING', 'true').lower() == 'true'
        self.FILL_LATENCY_TRACKING = os.getenv('FILL_LATENCY_TRACKING', 'true').lower() == 'true'
        self.REAL_VS_TESTNET_COMPARISON = os.getenv('REAL_VS_TESTNET_COMPARISON', 'true').lower() == 'true'
        self.MAX_LATENCY_MS = float(os.getenv('MAX_LATENCY_MS', '1500'))
        self.MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '2'))
        self.PAUSE_AFTER_FAILURE_MIN = int(os.getenv('PAUSE_AFTER_FAILURE_MIN', '15'))
        
        # === FASE 1.6: VALIDACIONES ===
        self.DAILY_REPORT_ENABLED = os.getenv('DAILY_REPORT_ENABLED', 'true').lower() == 'true'
        self.READY_TO_SCALE_THRESHOLD_PF = float(os.getenv('READY_TO_SCALE_THRESHOLD_PF', '1.5'))
        self.READY_TO_SCALE_THRESHOLD_DD = float(os.getenv('READY_TO_SCALE_THRESHOLD_DD', '0.5'))
        self.READY_TO_SCALE = os.getenv('READY_TO_SCALE', 'false').lower() == 'true'
        
        # === FASE 1.6: OPCIONALES ===
        self.BREAKEVEN_ENABLED = os.getenv('BREAKEVEN_ENABLED', 'false').lower() == 'true'
        self.DAILY_SUMMARY_ENABLED = os.getenv('DAILY_SUMMARY_ENABLED', 'true').lower() == 'true'
        self.DAILY_SUMMARY_TIME = os.getenv('DAILY_SUMMARY_TIME', '22:05 Europe/Madrid')
        
        # === FASE 1.6: CREDENCIALES ===
        self.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
        self.BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'your_secret_key_here')
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_token_here')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'your_chat_id_here')
        self.GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'your_google_sheets_credentials_here')
        self.GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', 'your_spreadsheet_id_here')
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtener resumen de configuración FASE 1.6"""
        return {
            'mode': self.MODE,
            'live_trading': self.LIVE_TRADING,
            'shadow_mode': self.SHADOW_MODE,
            'symbol': self.SYMBOL,
            'position_percent': self.POSITION_PERCENT,
            'tp_mode': self.TP_MODE,
            'tp_min_bps': self.TP_MIN_BPS,
            'min_range_bps': self.MIN_RANGE_BPS,
            'max_spread_bps': self.MAX_SPREAD_BPS,
            'min_vol_usd': self.MIN_VOL_USD,
            'max_ws_latency_ms': self.MAX_WS_LATENCY_MS,
            'max_rest_latency_ms': self.MAX_REST_LATENCY_MS,
            'fee_taker_bps': self.FEE_TAKER_BPS,
            'fee_maker_bps': self.FEE_MAKER_BPS,
            'slippage_bps': self.SLIPPAGE_BPS,
            'tp_buffer_bps': self.TP_BUFFER_BPS
        }
    
    def validate_config(self) -> bool:
        """Validar configuración FASE 1.6"""
        try:
            # Validar TP mínimo > fricción
            fee_bps = max(self.FEE_TAKER_BPS, self.FEE_MAKER_BPS)
            fric_bps = 2 * fee_bps + self.SLIPPAGE_BPS
            tp_floor = fric_bps + self.TP_BUFFER_BPS
            
            if self.TP_MIN_BPS < tp_floor:
                print(f"❌ TP_MIN_BPS ({self.TP_MIN_BPS}) < tp_floor ({tp_floor})")
                return False
            
            # Validar filtros
            if self.MIN_RANGE_BPS <= 0:
                print(f"❌ MIN_RANGE_BPS debe ser > 0")
                return False
            
            if self.MAX_SPREAD_BPS <= 0:
                print(f"❌ MAX_SPREAD_BPS debe ser > 0")
                return False
            
            if self.MIN_VOL_USD <= 0:
                print(f"❌ MIN_VOL_USD debe ser > 0")
                return False
            
            # Validar latencia
            if self.MAX_WS_LATENCY_MS <= 0:
                print(f"❌ MAX_WS_LATENCY_MS debe ser > 0")
                return False
            
            if self.MAX_REST_LATENCY_MS <= 0:
                print(f"❌ MAX_REST_LATENCY_MS debe ser > 0")
                return False
            
            print(f"✅ Configuración FASE 1.6 válida")
            print(f"📊 TP mínimo: {self.TP_MIN_BPS} bps")
            print(f"📊 Fricción: {fric_bps} bps")
            print(f"📊 TP floor: {tp_floor} bps")
            return True
            
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False

# Instancia global
config = Fase16Config()

if __name__ == "__main__":
    """Validar configuración al ejecutar directamente"""
    if config.validate_config():
        print("🎉 Configuración FASE 1.6 válida")
        print("📊 Resumen:", config.get_config_summary())
    else:
        print("❌ Configuración FASE 1.6 inválida")
        exit(1)
