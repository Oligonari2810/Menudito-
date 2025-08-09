#!/usr/bin/env python3
"""
⚙️ CONFIGURACIÓN FASE 1.6 - V1 BLOQUEADA + AUTO PAIR SELECTOR
Archivo de configuración centralizada para todas las variables de FASE 1.6
MULTI-PAR: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
AUTO PAIR SELECTOR: Selección automática de mejores pares en tendencia
"""

import os
from typing import Dict, Any, List, Optional
import sys

class Fase16Config:
    """Configuración centralizada FASE 1.6 - V1 BLOQUEADA + AUTO PAIR SELECTOR"""
    
    def __init__(self):
        # === FASE 1.6: FLAGS Y ENTORNO ===
        self.MODE = os.getenv('MODE', 'production')
        self.LIVE_TRADING = os.getenv('LIVE_TRADING', 'true').lower() == 'true'
        self.SHADOW_MODE = os.getenv('SHADOW_MODE', 'true').lower() == 'true'
        self.SESSION_WINDOW = os.getenv('SESSION_WINDOW', '09:00-22:00 Europe/Madrid')
        self.TIMEZONE = os.getenv('TIMEZONE', 'Europe/Madrid')
        
        # === FASE 1.6: MULTI-PAR CONFIGURACIÓN ===
        self.SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']  # 4 pares activos
        self.SYMBOL = os.getenv('SYMBOL', 'BNBUSDT')  # Default para compatibilidad
        self.CURRENT_SYMBOL_INDEX = 0  # Índice del símbolo actual
        
        # === AUTO PAIR SELECTOR ===
        self.AUTO_PAIR_SELECTOR = os.getenv('AUTO_PAIR_SELECTOR', 'true').lower() == 'true'  # ACTIVADO
        self.PAIRS_CANDIDATES = os.getenv('PAIRS_CANDIDATES', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,TONUSDT,MATICUSDT,ARBUSDT,OPUSDT,LTCUSDT,APTUSDT,TRXUSDT').split(',')
        self.MAX_ACTIVE_PAIRS = int(os.getenv('MAX_ACTIVE_PAIRS', '4'))
        self.REBALANCE_MINUTES = int(os.getenv('REBALANCE_MINUTES', '60'))
        self.LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '24'))
        
        # === AUTO PAIR SELECTOR: FILTROS MÍNIMOS ===
        self.CAND_MIN_24H_VOLUME_USD = float(os.getenv('CAND_MIN_24H_VOLUME_USD', '100000000'))  # 100M USD
        self.CAND_MIN_ATR_BPS = float(os.getenv('CAND_MIN_ATR_BPS', '12.0'))  # 0.12% (REDUCIDO de 15.0)
        self.CAND_MAX_SPREAD_BPS = float(os.getenv('CAND_MAX_SPREAD_BPS', '2.0'))  # 0.02%
        self.CAND_MIN_TREND_SCORE = float(os.getenv('CAND_MIN_TREND_SCORE', '0.60'))  # 0.6
        self.CAND_MAX_CORRELATION = float(os.getenv('CAND_MAX_CORRELATION', '0.85'))  # 0.85
        
        # === AUTO PAIR SELECTOR: SEGURIDAD DE CAMBIO ===
        self.DO_NOT_SWITCH_IF_POSITION_OPEN = os.getenv('DO_NOT_SWITCH_IF_POSITION_OPEN', 'true').lower() == 'true'
        self.MIN_HOURS_BETWEEN_SWITCHES = int(os.getenv('MIN_HOURS_BETWEEN_SWITCHES', '2'))
        
        # === AUTO PAIR SELECTOR: FALLBACK ===
        self.ENABLE_MULTI_PAIR = os.getenv('ENABLE_MULTI_PAIR', 'true').lower() == 'true'
        self.FALLBACK_PAIRS = os.getenv('PAIRS', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT').split(',')
        
        # === FASE 1.6: RIESGO (V1 BLOQUEADA) ===
        self.POSITION_SIZING_MODE = os.getenv('POSITION_SIZING_MODE', 'percent_of_equity')
        self.POSITION_PERCENT = float(os.getenv('POSITION_PERCENT', '0.10'))  # 0.10% bloqueado
        self.MIN_NOTIONAL_USD = float(os.getenv('MIN_NOTIONAL_USD', '5'))
        self.DAILY_MAX_DRAWDOWN_PCT = float(os.getenv('DAILY_MAX_DRAWDOWN_PCT', '0.50'))  # 0.5% bloqueado
        self.WEEKLY_MAX_DRAWDOWN_PCT = float(os.getenv('WEEKLY_MAX_DRAWDOWN_PCT', '1.50'))
        self.MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '2'))
        self.MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', '6'))  # Reducido a 6
        self.COOLDOWN_AFTER_LOSS_MIN = int(os.getenv('COOLDOWN_AFTER_LOSS_MIN', '30'))
        
        # === FASE 1.6: FEES/SLIPPAGE (V1 BLOQUEADA) ===
        self.FEE_TAKER_BPS = float(os.getenv('FEE_TAKER_BPS', '7.5'))
        self.FEE_MAKER_BPS = float(os.getenv('FEE_MAKER_BPS', '2.0'))
        self.SLIPPAGE_BPS = float(os.getenv('SLIPPAGE_BPS', '1.5'))
        self.TP_BUFFER_BPS = float(os.getenv('TP_BUFFER_BPS', '4.0'))  # 4.0 bloqueado
        
        # === FASE 1.6: OBJETIVOS DE SALIDA (V1 BLOQUEADA) ===
        self.TP_MODE = os.getenv('TP_MODE', 'fixed_min')
        self.TP_MIN_BPS = float(os.getenv('TP_MIN_BPS', '22.0'))  # 22.0 bloqueado
        self.ATR_PERIOD = int(os.getenv('ATR_PERIOD', '14'))
        self.TP_ATR_MULT = float(os.getenv('TP_ATR_MULT', '0.50'))
        self.SL_ATR_MULT = float(os.getenv('SL_ATR_MULT', '0.40'))
        
        # === FASE 1.6: FILTROS DE ENTRADA (V1 BLOQUEADA) ===
        self.MIN_RANGE_BPS = float(os.getenv('MIN_RANGE_BPS', '5.0'))  # 5.0 bloqueado
        self.MAX_SPREAD_BPS = float(os.getenv('MAX_SPREAD_BPS', '2.0'))  # 2.0 bloqueado
        self.MIN_VOL_USD = float(os.getenv('MIN_VOL_USD', '5000000'))  # 5M bloqueado
        self.ATR_MIN_PCT = float(os.getenv('ATR_MIN_PCT', '0.033'))  # 0.033% (REDUCIDO de 0.041)
        
        # === FASE 1.6: LATENCIA/ESTABILIDAD (V1 BLOQUEADA) ===
        self.MAX_WS_LATENCY_MS = float(os.getenv('MAX_WS_LATENCY_MS', '1500'))  # 1500ms bloqueado
        self.MAX_REST_LATENCY_MS = float(os.getenv('MAX_REST_LATENCY_MS', '800'))  # 800ms bloqueado
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
        
        # === FASE 1.6: RESUMEN DIARIO ===
        self.DAILY_SUMMARY_ENABLED = os.getenv('DAILY_SUMMARY_ENABLED', 'true').lower() == 'true'
        self.DAILY_SUMMARY_TIME = os.getenv('DAILY_SUMMARY_TIME', '22:05 Europe/Madrid')
        
        # === FASE 1.6: OPCIONALES ===
        self.BREAKEVEN_ENABLED = os.getenv('BREAKEVEN_ENABLED', 'false').lower() == 'true'
        
        # === FASE 1.6: CONFIGURACIÓN ADICIONAL ===
        self.CYCLE_INTERVAL_SECONDS = int(os.getenv('CYCLE_INTERVAL_SECONDS', '180'))
        self.MAKER_ONLY = os.getenv('MAKER_ONLY', 'true').lower() == 'true'
        self.SPREAD_ADAPTIVE = os.getenv('SPREAD_ADAPTIVE', 'true').lower() == 'true'
        self.POSITION_SIZE_USD_MIN = float(os.getenv('POSITION_SIZE_USD_MIN', '2.00'))
        
        # === FASE 1.6: CREDENCIALES ===
        self.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
        self.BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'your_secret_key_here')
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_token_here')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'your_chat_id_here')
        self.GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'your_google_sheets_credentials_here')
        self.GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', 'your_spreadsheet_id_here')
    
    def get_current_symbol(self) -> str:
        """Obtener símbolo actual del multi-par"""
        return self.SYMBOLS[self.CURRENT_SYMBOL_INDEX]
    
    def rotate_symbol(self) -> str:
        """Rotar al siguiente símbolo del multi-par"""
        self.CURRENT_SYMBOL_INDEX = (self.CURRENT_SYMBOL_INDEX + 1) % len(self.SYMBOLS)
        return self.get_current_symbol()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtener resumen de configuración FASE 1.6 - V1 BLOQUEADA + AUTO PAIR SELECTOR"""
        return {
            'mode': self.MODE,
            'live_trading': self.LIVE_TRADING,
            'shadow_mode': self.SHADOW_MODE,
            'symbols': self.SYMBOLS,
            'current_symbol': self.get_current_symbol(),
            'auto_pair_selector': self.AUTO_PAIR_SELECTOR,
            'pairs_candidates': len(self.PAIRS_CANDIDATES),
            'max_active_pairs': self.MAX_ACTIVE_PAIRS,
            'rebalance_minutes': self.REBALANCE_MINUTES,
            'position_percent': self.POSITION_PERCENT,
            'tp_mode': self.TP_MODE,
            'tp_min_bps': self.TP_MIN_BPS,
            'min_range_bps': self.MIN_RANGE_BPS,
            'max_spread_bps': self.MAX_SPREAD_BPS,
            'min_vol_usd': self.MIN_VOL_USD,
            'atr_min_pct': self.ATR_MIN_PCT,
            'max_ws_latency_ms': self.MAX_WS_LATENCY_MS,
            'max_rest_latency_ms': self.MAX_REST_LATENCY_MS,
            'fee_taker_bps': self.FEE_TAKER_BPS,
            'fee_maker_bps': self.FEE_MAKER_BPS,
            'slippage_bps': self.SLIPPAGE_BPS,
            'tp_buffer_bps': self.TP_BUFFER_BPS,
            'max_trades_per_day': self.MAX_TRADES_PER_DAY,
            'daily_max_drawdown_pct': self.DAILY_MAX_DRAWDOWN_PCT
        }
    
    def validate_config(self) -> bool:
        """Validar configuración FASE 1.6 - V1 BLOQUEADA + AUTO PAIR SELECTOR"""
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
            
            # Validar símbolos
            if not self.SYMBOLS:
                print(f"❌ SYMBOLS no puede estar vacío")
                return False
            
            # Validar Auto Pair Selector
            if self.AUTO_PAIR_SELECTOR:
                if not self.PAIRS_CANDIDATES:
                    print(f"❌ PAIRS_CANDIDATES no puede estar vacío si AUTO_PAIR_SELECTOR=true")
                    return False
                
                if self.MAX_ACTIVE_PAIRS <= 0:
                    print(f"❌ MAX_ACTIVE_PAIRS debe ser > 0")
                    return False
                
                if self.REBALANCE_MINUTES <= 0:
                    print(f"❌ REBALANCE_MINUTES debe ser > 0")
                    return False
            
            print("✅ Configuración FASE 1.6 + AUTO PAIR SELECTOR válida")
            print(f"📊 TP mínimo: {self.TP_MIN_BPS} bps")
            print(f"📊 Fricción: {fric_bps} bps")
            print(f"📊 TP floor: {tp_floor} bps")
            print(f"📊 Símbolos: {', '.join(self.SYMBOLS)}")
            print(f"🎯 Auto Pair Selector: {'✅ ACTIVO' if self.AUTO_PAIR_SELECTOR else '❌ INACTIVO'}")
            if self.AUTO_PAIR_SELECTOR:
                print(f"📊 Candidatos: {len(self.PAIRS_CANDIDATES)} pares")
                print(f"🎯 Máximo activos: {self.MAX_ACTIVE_PAIRS}")
                print(f"🔄 Rebalance: {self.REBALANCE_MINUTES} min")
            return True
            
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False

# Instancia global de configuración
config = Fase16Config()

if __name__ == "__main__":
    # Validar configuración al ejecutar directamente
    if config.validate_config():
        print("\n🎯 CONFIGURACIÓN FASE 1.6 - V1 BLOQUEADA + AUTO PAIR SELECTOR")
        print("=" * 70)
        summary = config.get_config_summary()
        for key, value in summary.items():
            print(f"📊 {key}: {value}")
        print("\n✅ Configuración lista para producción")
    else:
        print("\n❌ Configuración inválida")
        sys.exit(1)
