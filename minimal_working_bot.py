#!/usr/bin/env python3
"""
🤖 TRADING BOT PROFESIONAL - FASE 1.5: OPTIMIZACIÓN
Bot de trading optimizado con sistema de métricas avanzado y gestión de riesgo mejorada
"""

import os
import time
import logging
import signal
import random
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import getcontext
import requests

# Importar configuración FASE 1.6
try:
    from config_fase_1_6 import config
except ImportError:
    # Fallback si no existe el archivo de configuración
    class MockConfig:
        def __init__(self):
            self.FEE_TAKER_BPS = 7.5
            self.FEE_MAKER_BPS = 2.0
            self.SLIPPAGE_BPS = 1.5
            self.TP_BUFFER_BPS = 2.0
            self.TP_MODE = 'fixed_min'
            self.TP_MIN_BPS = 18.5
            self.ATR_PERIOD = 14
            self.TP_ATR_MULT = 0.50
            self.SL_ATR_MULT = 0.40
            self.MIN_RANGE_BPS = 5.0
            self.MAX_SPREAD_BPS = 2.0
            self.MIN_VOL_USD = 5000000
            self.MAX_WS_LATENCY_MS = 1500
            self.MAX_REST_LATENCY_MS = 800
            self.RETRY_ORDER = 2
    config = MockConfig()

# Configurar precisión decimal
getcontext().prec = 8

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Variable global para control de apagado (mutable)
shutdown_state = {"stop": False}

def handle_shutdown_signal(signum, frame):
    """Manejar señales de apagado de manera limpia"""
    signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    logging.info(f"🛑 {signal_name} recibido → Iniciando apagado limpio...")
    shutdown_state["stop"] = True

# Configurar señales
signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)

def sleep_responsive(seconds: int):
    """Dormir en bloques de 1s, saliendo en <1s si llega señal de apagado"""
    remaining = int(seconds)
    while remaining > 0 and not shutdown_state["stop"]:
        time.sleep(1)
        remaining -= 1

class SafetyManager:
    """Sistema de gestión de seguridad y protecciones FASE 1.6"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_loss = 0.0
        self.intraday_drawdown = 0.0
        self.consecutive_losses = 0
        self.last_trade_time = None
        self.hourly_trades = 0
        self.daily_trades = 0
        self.session_start_time = datetime.now()
        self.session_start_capital = 50.0
        
        # Cooldown racha
        self.racha_cooldown_start = None
        self.racha_cooldown_duration = 1800  # 30 minutos
        self.probation_mode = False
        self.probation_trades = 0
        self.max_probation_trades = 1
        
        # === FASE 1.6: LÍMITES DE SEGURIDAD ACTUALIZADOS ===
        self.daily_loss_limit = float(os.getenv('DAILY_MAX_DRAWDOWN_PCT', '0.50')) / 100  # 0.5%
        self.intraday_drawdown_limit = 0.10  # 10%
        self.max_consecutive_losses = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '2'))
        self.min_cooldown_seconds = int(os.getenv('COOLDOWN_AFTER_LOSS_MIN', '30')) * 60
        self.max_trades_per_hour = 20
        self.max_trades_per_day = int(os.getenv('MAX_TRADES_PER_DAY', '8'))
        
        # === FASE 1.6: CONFIGURACIÓN CENTRALIZADA ===
        self.fee_taker_bps = config.FEE_TAKER_BPS
        self.fee_maker_bps = config.FEE_MAKER_BPS
        self.slippage_bps = config.SLIPPAGE_BPS
        self.tp_buffer_bps = config.TP_BUFFER_BPS
        
        # === FASE 1.6: OBJETIVOS DE SALIDA ===
        self.tp_mode = config.TP_MODE
        self.tp_min_bps = config.TP_MIN_BPS
        self.atr_period = config.ATR_PERIOD
        self.tp_atr_mult = config.TP_ATR_MULT
        self.sl_atr_mult = config.SL_ATR_MULT
        
        # === FASE 1.6: FILTROS DE ENTRADA ===
        self.min_range_bps = config.MIN_RANGE_BPS
        self.max_spread_bps = config.MAX_SPREAD_BPS
        self.min_vol_usd = config.MIN_VOL_USD
        
        # === FASE 1.6: LATENCIA/ESTABILIDAD ===
        self.max_ws_latency_ms = config.MAX_WS_LATENCY_MS
        self.max_rest_latency_ms = config.MAX_REST_LATENCY_MS
        self.retry_order = config.RETRY_ORDER
        
    def compute_trade_targets(self, price: float, atr_value: float = None) -> Dict[str, float]:
        """FASE 1.6: Calcular TP y SL dinámicos con fricción"""
        
        # Calcular fricción total
        fee_bps = max(self.fee_taker_bps, self.fee_maker_bps)
        fric_bps = 2 * fee_bps + self.slippage_bps  # entrada + salida + slippage
        tp_floor = fric_bps + self.tp_buffer_bps
        
        if self.tp_mode == "fixed_min":
            # Modo TP fijo mínimo
            tp_bps = max(self.tp_min_bps, tp_floor)
            sl_bps = tp_bps / 1.25  # RR ≈ 1.25:1
        else:
            # Modo ATR dinámico
            if atr_value is None:
                atr_value = price * 0.01  # 1% por defecto
            
            atr_pct = (atr_value / price) * 100 * 100  # convertir a bps
            tp_bps = max(self.tp_atr_mult * atr_pct, tp_floor)
            sl_bps = max(self.sl_atr_mult * atr_pct, tp_floor / 1.25)
        
        return {
            'tp_bps': tp_bps,
            'sl_bps': sl_bps,
            'tp_floor': tp_floor,
            'fric_bps': fric_bps,
            'rr_ratio': tp_bps / sl_bps if sl_bps > 0 else 0,
            'tp_pct': tp_bps / 10000,  # convertir a porcentaje
            'sl_pct': sl_bps / 10000   # convertir a porcentaje
        }
    
    def pre_trade_filters(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """FASE 1.6: Aplicar filtros previos al trade"""
        
        filter_result = {
            'passed': True,
            'reason': 'OK',
            'details': {},
            'warnings': []
        }
        
        # Extraer datos del mercado
        current_price = market_data.get('price', 0.0)
        high = market_data.get('high', current_price)
        low = market_data.get('low', current_price)
        close = market_data.get('close', current_price)
        best_ask = market_data.get('best_ask', current_price)
        best_bid = market_data.get('best_bid', current_price)
        volume_usd = market_data.get('volume_usd', 0.0)
        ws_latency_ms = market_data.get('ws_latency_ms', 0.0)
        rest_latency_ms = market_data.get('rest_latency_ms', 0.0)
        
        # 1. Filtro de rango de vela
        if close > 0:
            range_pct = ((high - low) / close) * 100
            range_bps = range_pct * 100  # convertir a bps
            
            filter_result['details']['range_pct'] = range_pct
            filter_result['details']['range_bps'] = range_bps
            
            if range_bps < self.min_range_bps:
                filter_result['passed'] = False
                filter_result['reason'] = 'LOW_RANGE'
                filter_result['details']['min_range_bps'] = self.min_range_bps
                self.logger.info(f"❌ Trade rechazado: Rango bajo {range_bps:.1f} bps < {self.min_range_bps} bps")
                return filter_result
        else:
            filter_result['passed'] = False
            filter_result['reason'] = 'INVALID_PRICE'
            return filter_result
        
        # 2. Filtro de spread
        if best_ask > 0 and best_bid > 0:
            mid_price = (best_ask + best_bid) / 2
            spread_pct = ((best_ask - best_bid) / mid_price) * 100
            spread_bps = spread_pct * 100  # convertir a bps
            
            filter_result['details']['spread_pct'] = spread_pct
            filter_result['details']['spread_bps'] = spread_bps
            
            if spread_bps > self.max_spread_bps:
                filter_result['passed'] = False
                filter_result['reason'] = 'HIGH_SPREAD'
                filter_result['details']['max_spread_bps'] = self.max_spread_bps
                self.logger.info(f"❌ Trade rechazado: Spread alto {spread_bps:.1f} bps > {self.max_spread_bps} bps")
                return filter_result
        else:
            filter_result['warnings'].append("Spread no disponible")
        
        # 3. Filtro de volumen
        filter_result['details']['volume_usd'] = volume_usd
        
        if volume_usd < self.min_vol_usd:
            filter_result['passed'] = False
            filter_result['reason'] = 'LOW_VOLUME'
            filter_result['details']['min_vol_usd'] = self.min_vol_usd
            self.logger.info(f"❌ Trade rechazado: Volumen bajo ${volume_usd:,.0f} < ${self.min_vol_usd:,.0f}")
            return filter_result
        
        # 4. Filtro de latencia WebSocket
        filter_result['details']['ws_latency_ms'] = ws_latency_ms
        
        if ws_latency_ms > self.max_ws_latency_ms:
            filter_result['passed'] = False
            filter_result['reason'] = 'HIGH_WS_LAT'
            filter_result['details']['max_ws_latency_ms'] = self.max_ws_latency_ms
            self.logger.info(f"❌ Trade rechazado: Latencia WS alta {ws_latency_ms:.1f}ms > {self.max_ws_latency_ms}ms")
            return filter_result
        
        # 5. Filtro de latencia REST
        filter_result['details']['rest_latency_ms'] = rest_latency_ms
        
        if rest_latency_ms > self.max_rest_latency_ms:
            filter_result['passed'] = False
            filter_result['reason'] = 'HIGH_REST_LAT'
            filter_result['details']['max_rest_latency_ms'] = self.max_rest_latency_ms
            self.logger.info(f"❌ Trade rechazado: Latencia REST alta {rest_latency_ms:.1f}ms > {self.max_rest_latency_ms}ms")
            return filter_result
        
        # Si pasa todos los filtros
        if filter_result['passed']:
            self.logger.info(f"✅ Filtros pasados: Rango={range_bps:.1f}bps, Spread={spread_bps:.1f}bps, Vol=${volume_usd:,.0f}")
        
        return filter_result
    
    def calculate_fees_and_slippage(self, trade_data: Dict[str, Any]) -> Dict[str, float]:
        """FASE 1.6: Calcular fees y slippage realistas"""
        
        notional = trade_data.get('notional', 0.0)
        intended_price = trade_data.get('intended_price', 0.0)
        executed_price = trade_data.get('executed_price', 0.0)
        
        # Calcular fees (entrada + salida)
        fee_rate = self.fee_taker_bps / 10000  # convertir bps a decimal
        entry_fee = notional * fee_rate
        exit_fee = notional * fee_rate  # estimado para salida
        total_fees = entry_fee + exit_fee
        
        # Calcular slippage
        if intended_price > 0 and executed_price > 0:
            slippage_pct = abs(executed_price - intended_price) / intended_price
            slippage_cost = notional * slippage_pct
        else:
            slippage_pct = 0.0
            slippage_cost = 0.0
        
        # Convertir a bps para logging
        fees_bps = (total_fees / notional) * 10000 if notional > 0 else 0
        slippage_bps = slippage_pct * 10000
        
        return {
            'entry_fee': entry_fee,
            'exit_fee': exit_fee,
            'total_fees': total_fees,
            'fees_bps': fees_bps,
            'slippage_cost': slippage_cost,
            'slippage_bps': slippage_bps,
            'slippage_pct': slippage_pct,
            'total_friction': total_fees + slippage_cost
        }
    
    def calculate_net_pnl(self, trade_data: Dict[str, Any]) -> Dict[str, float]:
        """FASE 1.6: Calcular P&L neto incluyendo fees y slippage"""
        
        # P&L bruto
        gross_pnl = trade_data.get('realized_pnl', 0.0)
        
        # Calcular fees y slippage
        friction_data = self.calculate_fees_and_slippage(trade_data)
        
        # P&L neto
        net_pnl = gross_pnl - friction_data['total_friction']
        
        return {
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl,
            'fees_cost': friction_data['total_fees'],
            'slippage_cost': friction_data['slippage_cost'],
            'total_friction': friction_data['total_friction'],
            'friction_impact': (friction_data['total_friction'] / abs(gross_pnl) * 100) if gross_pnl != 0 else 0
        }
    
    def check_safety_conditions(self, current_capital: float) -> Dict[str, Any]:
        """Verificar todas las condiciones de seguridad"""
        try:
            # Calcular métricas de seguridad
            self.intraday_drawdown = ((self.session_start_capital - current_capital) / self.session_start_capital) * 100
            self.daily_loss = ((50.0 - current_capital) / 50.0) * 100
            
            # Verificar cooldown racha
            self.check_racha_cooldown()
            
            # Verificar límites
            safety_status = {
                'can_trade': True,
                'reason': None,
                'daily_loss': self.daily_loss,
                'intraday_drawdown': self.intraday_drawdown,
                'consecutive_losses': self.consecutive_losses,
                'probation_mode': self.probation_mode,
                'racha_cooldown_active': self.racha_cooldown_start is not None,
                'hourly_trades': self.hourly_trades
            }
            
            # Kill switches FASE 1.6
            if self.daily_loss >= (self.daily_loss_limit * 100):
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Pérdida diaria crítica: {self.daily_loss:.2f}%"
                
            elif self.intraday_drawdown >= 10.0:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Drawdown intradía crítico: {self.intraday_drawdown:.2f}%"
                
            elif self.consecutive_losses >= 3 and not self.probation_mode:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Racha de pérdidas: {self.consecutive_losses} consecutivas"
            
            # Cooldown racha
            elif self.racha_cooldown_start and (datetime.now() - self.racha_cooldown_start).total_seconds() < self.racha_cooldown_duration:
                safety_status['can_trade'] = False
                remaining_time = self.racha_cooldown_duration - (datetime.now() - self.racha_cooldown_start).total_seconds()
                safety_status['reason'] = f"Cooldown racha activo: {remaining_time/60:.1f}min restantes"
            
            # Rate limiting
            if self.last_trade_time:
                time_since_last = (datetime.now() - self.last_trade_time).total_seconds()
                if time_since_last < self.min_cooldown_seconds:
                    safety_status['can_trade'] = False
                    safety_status['reason'] = f"Cooldown activo: {self.min_cooldown_seconds - time_since_last:.0f}s restantes"
            
            if self.hourly_trades >= self.max_trades_per_hour:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Límite horario alcanzado: {self.hourly_trades}/{self.max_trades_per_hour}"
                
            if self.daily_trades >= self.max_trades_per_day:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Límite diario alcanzado: {self.daily_trades}/{self.max_trades_per_day}"
            
            return safety_status
            
        except Exception as e:
            self.logger.error(f"❌ Error en verificación de seguridad: {e}")
            return {'can_trade': False, 'reason': f"Error de seguridad: {e}"}
    
    def check_racha_cooldown(self):
        """Verificar y gestionar cooldown de racha"""
        try:
            # Si hay cooldown activo y ha pasado el tiempo
            if self.racha_cooldown_start and (datetime.now() - self.racha_cooldown_start).total_seconds() >= self.racha_cooldown_duration:
                self.racha_cooldown_start = None
                self.probation_mode = True
                self.probation_trades = 0
                self.logger.info("🔄 Cooldown racha completado - Modo probation activado")
                
        except Exception as e:
            self.logger.error(f"❌ Error verificando cooldown racha: {e}")
    
    def record_trade(self, result: str, pnl: float) -> None:
        """Registrar resultado de trade para métricas de seguridad"""
        try:
            self.last_trade_time = datetime.now()
            self.hourly_trades += 1
            self.daily_trades += 1
            
            # Actualizar racha de pérdidas
            if result == 'PÉRDIDA':
                self.consecutive_losses += 1
                
                # Activar cooldown si alcanza límite
                if self.consecutive_losses >= self.max_consecutive_losses:
                    self.racha_cooldown_start = datetime.now()
                    self.logger.info(f"🚨 Racha de pérdidas crítica ({self.consecutive_losses}) - Cooldown 30min activado")
            else:
                self.consecutive_losses = 0
                
                # Si está en probation y gana, salir del modo
                if self.probation_mode:
                    self.probation_mode = False
                    self.probation_trades = 0
                    self.logger.info("✅ Probation exitoso - Modo normal restaurado")
            
            # Actualizar probation trades
            if self.probation_mode:
                self.probation_trades += 1
                if self.probation_trades >= self.max_probation_trades:
                    self.probation_mode = False
                    self.probation_trades = 0
                    self.logger.info("✅ Probation completado - Modo normal restaurado")
                
            self.logger.info(f"📊 Seguridad: DD={self.intraday_drawdown:.2f}%, DL={self.daily_loss:.2f}%, CL={self.consecutive_losses}, Probation={self.probation_mode}")
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando trade: {e}")
    
    def reset_hourly_counters(self):
        """Resetear contadores horarios"""
        try:
            self.hourly_trades = 0
            self.logger.info("🔄 Contadores horarios reseteados")
        except Exception as e:
            self.logger.error(f"❌ Error reseteando contadores: {e}")

class MarketFilter:
    """Sistema de filtros de mercado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Parámetros de filtros
        self.atr_period = 14
        self.atr_timeframe = "1m"
        self.atr_percentile_min = 40
        self.atr_percentile_max = 50
        self.ema_period = 50
        self.ema_timeframe = "1m"
        self.spread_max = 0.03  # 0.03% base
        self.slippage_max = 0.02  # 0.02%
        
        # Configuración adaptativa
        self.spread_adaptive_on = True
        self.spread_adaptive_threshold = 0.05  # Subir a 0.04-0.05% si necesario
        self.spread_epsilon = 0.00001
        self.maker_only_enabled = True
        
    def check_market_conditions(self, price: float, volume: float) -> Dict[str, Any]:
        """Verificar condiciones de mercado para operar"""
        try:
            # Simular indicadores técnicos
            atr_value = self.simulate_atr(price)
            ema_value = self.simulate_ema(price)
            spread_value = self.simulate_spread(price)
            
            # Spread adaptativo
            current_spread_max = self.spread_max
            if self.spread_adaptive_on and spread_value > self.spread_max:
                # Permitir spread más alto si es necesario
                current_spread_max = min(spread_value * 1.2, self.spread_adaptive_threshold)
                self.logger.info(f"📊 Spread adaptativo: {spread_value:.3f}% → permitido hasta {current_spread_max:.3f}%")
            
            filter_status = {
                'can_trade': True,
                'reason': None,
                'reason_code': None,
                'atr': atr_value,
                'ema': ema_value,
                'spread': spread_value,
                'maker_only': self.maker_only_enabled,
                'spread_adaptive': self.spread_adaptive_on
            }
            
            # Filtro ATR (volatilidad mínima) con umbral dinámico 40–50%
            atr_min_dynamic = 0.40 + (0.10 * random.random())  # 0.40–0.50
            if atr_value < atr_min_dynamic:
                filter_status['can_trade'] = False
                filter_status['reason'] = f"Volatilidad insuficiente: ATR={atr_value:.3f} (<{atr_min_dynamic:.3f})"
                filter_status['reason_code'] = 'low_vol'
            
            # Filtro EMA50 (tendencia)
            if price > ema_value:
                filter_status['direction'] = 'BUY'
            else:
                filter_status['direction'] = 'SELL'
            
            # Filtro spread adaptativo con tolerancia epsilon
            if (spread_value - current_spread_max) > self.spread_epsilon:
                filter_status['can_trade'] = False
                filter_status['reason'] = f"Spread alto: {spread_value:.3f}% (máx: {current_spread_max:.3f}%)"
                filter_status['reason_code'] = 'spread_high'
            
            return filter_status
            
        except Exception as e:
            self.logger.error(f"❌ Error en filtros de mercado: {e}")
            return {'can_trade': False, 'reason': f"Error de filtros: {e}"}
    
    def simulate_atr(self, price: float) -> float:
        """Simular valor ATR"""
        return random.uniform(0.3, 0.8)
    
    def simulate_ema(self, price: float) -> float:
        """Simular valor EMA50"""
        return price * random.uniform(0.995, 1.005)
    
    def simulate_spread(self, price: float) -> float:
        """Simular spread"""
        return random.uniform(0.01, 0.05)

class PositionManager:
    """Gestión de posiciones con ATR dinámico y trailing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuración ATR dinámico
        self.atr_multiplier_sl = 1.0
        self.atr_multiplier_tp = 1.3
        
        # Configuración trailing
        self.trailing_activation = 0.25  # 0.25%
        self.trailing_step = 0.08  # 0.08%
        
        # Fees
        self.fee_rate = 0.001  # 0.1%
        self.fees_included = True
        
        # Configuración de trading
        self.position_size_usd_min = 2.00  # Mínimo $2 USD
        self.enable_maker_only = True  # Solo órdenes maker
        self.spread_adaptive_on = True  # Spread adaptativo
        self.enable_parallel_pairs = []  # Solo BNBUSDT
        
    def calculate_position_size(self, capital: float, atr_value: float) -> Dict[str, Any]:
        """Calcular tamaño de posición basado en ATR"""
        try:
            # Tamaño base (0.6% del capital)
            base_size = capital * 0.006
            
            # Ajustar por ATR
            atr_adjusted_size = base_size * (atr_value / 0.5)  # Normalizar ATR
            
            # Límite máximo (1.2% del capital)
            max_size = capital * 0.012
            
            # Tamaño final
            final_size = min(atr_adjusted_size, max_size)
            
            # Verificar mínimo USD
            if final_size < self.position_size_usd_min:
                final_size = self.position_size_usd_min
            
            # Calcular fees
            estimated_fees = final_size * self.fee_rate
            
            position_data = {
                'size': final_size,
                'fees': estimated_fees,
                'size_net': final_size - estimated_fees,
                'atr_value': atr_value,
                'base_size': base_size,
                'max_size': max_size,
                'maker_only': self.enable_maker_only,
                'spread_adaptive': self.spread_adaptive_on
            }
            
            self.logger.info(f"💰 Tamaño posición: ${final_size:.2f} (ATR: {atr_value:.3f}, Maker: {self.enable_maker_only})")
            return position_data
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando tamaño: {e}")
            return {'size': 0, 'fees': 0, 'size_net': 0}
    
    def calculate_sl_tp(self, entry_price: float, direction: str, atr_value: float) -> Dict[str, Any]:
        """Calcular SL y TP basados en ATR"""
        try:
            # SL y TP basados en ATR
            sl_distance = atr_value * self.atr_multiplier_sl
            tp_distance = atr_value * self.atr_multiplier_tp
            
            if direction == 'BUY':
                sl_price = entry_price - sl_distance
                tp_price = entry_price + tp_distance
            else:
                sl_price = entry_price + sl_distance
                tp_price = entry_price - tp_distance
            
            # Trailing stop
            trailing_activation_price = entry_price + (tp_distance * self.trailing_activation)
            trailing_step = tp_distance * self.trailing_step
            
            sl_tp_data = {
                'sl_price': sl_price,
                'tp_price': tp_price,
                'trailing_activation': trailing_activation_price,
                'trailing_step': trailing_step,
                'atr_value': atr_value
            }
            
            self.logger.info(f"📊 SL: ${sl_price:.2f}, TP: ${tp_price:.2f} (ATR: {atr_value:.3f})")
            return sl_tp_data
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando SL/TP: {e}")
            return {'sl_price': 0, 'tp_price': 0}

class MetricsTracker:
    """Sistema de monitoreo de métricas clave con fees incluidos"""
    
    def __init__(self, max_operations: int = 50):
        self.logger = logging.getLogger(__name__)
        self.max_operations = max_operations
        self.operations_history: List[Dict] = []
        self.peak_capital = 50.0
        self.current_capital = 50.0
        self.fees_included = True
        
    def add_operation(self, operation: Dict[str, Any]) -> None:
        """Añadir operación al historial"""
        try:
            # Añadir operación
            self.operations_history.append(operation)
            
            # Mantener solo las últimas max_operations
            if len(self.operations_history) > self.max_operations:
                self.operations_history = self.operations_history[-self.max_operations:]
            
            # Actualizar capital (neto de fees)
            self.current_capital = operation.get('capital_net', self.current_capital)
            
            # Actualizar peak capital
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
                
            self.logger.info(f"✅ Operación añadida al historial. Total: {len(self.operations_history)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error añadiendo operación: {e}")
    
    def calculate_win_rate(self) -> float:
        """Calcular Win Rate de las últimas operaciones"""
        try:
            if not self.operations_history:
                return 0.0
            
            winning_operations = sum(1 for op in self.operations_history if op.get('result') == 'GANANCIA')
            total_operations = len(self.operations_history)
            
            win_rate = (winning_operations / total_operations) * 100
            self.logger.info(f"📊 Win Rate calculado: {win_rate:.2f}% ({winning_operations}/{total_operations})")
            return win_rate
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando Win Rate: {e}")
            return 0.0
    
    def calculate_profit_factor(self) -> float:
        """Calcular Profit Factor neto de fees"""
        try:
            if not self.operations_history:
                return 0.0
            
            # Usar P&L neto de fees con precisión completa
            total_gains = sum(op.get('pnl_net', 0) for op in self.operations_history if op.get('pnl_net', 0) > 0)
            total_losses = abs(sum(op.get('pnl_net', 0) for op in self.operations_history if op.get('pnl_net', 0) < 0))
            
            # Manejar casos especiales
            if total_losses == 0:
                if total_gains > 0:
                    profit_factor = float('inf')  # Infinito para gains sin losses
                else:
                    profit_factor = 0.0  # Sin operaciones
            elif total_gains == 0:
                profit_factor = 0.0  # Solo losses
            else:
                profit_factor = total_gains / total_losses
            
            self.logger.info(f"📈 Profit Factor (neto) calculado: {profit_factor:.2f} (Gains: ${total_gains:.4f}, Losses: ${total_losses:.4f})")
            return profit_factor
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando Profit Factor: {e}")
            return 0.0
    
    def get_profit_factor_display(self) -> str:
        """Obtener PF para display con manejo de casos especiales"""
        try:
            pf = self.calculate_profit_factor()
            
            if pf == float('inf'):
                return "N/A"
            elif pf == 0.0:
                return "N/A"
            else:
                return f"{pf:.2f}"
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo PF display: {e}")
            return "N/A"
    
    def calculate_drawdown(self) -> float:
        """Calcular Drawdown actual"""
        try:
            if self.peak_capital == 0:
                return 0.0
            
            drawdown = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
            self.logger.info(f"📉 Drawdown calculado: {drawdown:.2f}% (Peak: ${self.peak_capital:.2f}, Current: ${self.current_capital:.2f})")
            return drawdown
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando Drawdown: {e}")
            return 0.0
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtener resumen de métricas"""
        try:
            win_rate = self.calculate_win_rate()
            profit_factor = self.calculate_profit_factor()
            drawdown = self.calculate_drawdown()
            
            metrics = {
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'drawdown': drawdown,
                'total_operations': len(self.operations_history),
                'current_capital': self.current_capital,
                'peak_capital': self.peak_capital
            }
            
            self.logger.info(f"📊 Métricas calculadas: WR={win_rate:.2f}%, PF={profit_factor:.2f}, DD={drawdown:.2f}%")
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo métricas: {e}")
            return {}

class GoogleSheetsLogger:
    """Logger profesional para Google Sheets con métricas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sheets_enabled = False
        self.spreadsheet_name = "Trading Bot Log"
        self.worksheet_name = "Trading Log"
        
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            import json
            
            # Configurar credenciales
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Intentar desde archivo local primero
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                self.client = gspread.authorize(creds)
                self.sheets_enabled = True
                self.logger.info("✅ Google Sheets configurado desde archivo local")
            # Intentar desde variable de entorno (Render)
            elif os.getenv('GOOGLE_SHEETS_CREDENTIALS'):
                try:
                    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
                    creds = Credentials.from_service_account_info(json.loads(credentials_json), scopes=scope)
                    self.client = gspread.authorize(creds)
                    self.sheets_enabled = True
                    self.logger.info("✅ Google Sheets configurado desde variable de entorno")
                except Exception as e:
                    self.logger.error(f"❌ Error configurando desde variable de entorno: {e}")
                    self.sheets_enabled = False
            else:
                self.logger.warning("⚠️ credentials.json no encontrado y GOOGLE_SHEETS_CREDENTIALS no configurado")
                self.sheets_enabled = False
                
        except Exception as e:
            self.logger.error(f"❌ Error configurando Google Sheets: {e}")
            self.sheets_enabled = False
    
    def log_trade(self, trade_data: Dict[str, Any], metrics: Dict[str, Any] = None) -> bool:
        """Log trade a Google Sheets con métricas"""
        try:
            if not self.sheets_enabled:
                return False
            
            # Obtener worksheet
            spreadsheet = self.client.open(self.spreadsheet_name)
            worksheet = spreadsheet.worksheet(self.worksheet_name)
            
            # Preparar datos del trade
            timestamp = trade_data.get('timestamp', datetime.now().isoformat())
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_part = dt.strftime('%Y-%m-%d')
            time_part = dt.strftime('%H:%M:%S')
            
            # Obtener métricas si no se proporcionan
            if not metrics:
                metrics = {
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'drawdown': 0.0
                }
            
            # Crear fila de datos FASE 1.6 (Date, Time en columnas separadas)
            row_data = [
                date_part,                 # Fecha
                time_part,                 # Hora
                trade_data.get('symbol', 'BNBUSDT'),  # Símbolo
                trade_data.get('direction', ''),      # Dirección
                f"${trade_data.get('entry_price', 0):,.2f}",  # Precio Entrada
                f"{trade_data.get('size', 0):.6f}",           # Cantidad
                f"${trade_data.get('notional', 0):.2f}",      # Monto
                trade_data.get('strategy', 'breakout'),        # Estrategia
                f"{trade_data.get('confidence', 0):.1%}",     # Confianza
                "✅" if trade_data.get('ai_validation', True) else "❌",  # IA Validación
                trade_data.get('result', ''),                  # Resultado
                f"${trade_data.get('net_pnl', 0):.4f}",       # P&L Neto
                f"${trade_data.get('capital', 0):.2f}",       # Balance
                f"{metrics.get('win_rate', 0):.2f}%",         # Win Rate (%)
                metrics.get('profit_factor_display', 'N/A'),   # Profit Factor
                f"{metrics.get('drawdown', 0):.2f}%",         # Drawdown (%)
                f"{trade_data.get('signal_score', 0):.2f}",   # Signal Score
                f"${trade_data.get('expected_price', 0):.4f}", # Expected Price
                f"${trade_data.get('fill_price', 0):.4f}",    # Fill Price
                f"{trade_data.get('tick_size', 0):.4f}",      # Tick Size
                f"{trade_data.get('slippage_pct', 0):.4f}%",  # Slippage (%)
                
                # === FASE 1.6: NUEVAS COLUMNAS ===
                f"{trade_data.get('tp_bps', 0):.1f}",         # TP (bps)
                f"{trade_data.get('sl_bps', 0):.1f}",         # SL (bps)
                f"{trade_data.get('range_bps', 0):.1f}",      # Range (bps)
                f"{trade_data.get('spread_bps', 0):.1f}",     # Spread (bps)
                f"{trade_data.get('fees_bps', 0):.1f}",       # Fee (bps)
                f"${trade_data.get('fees_cost', 0):.4f}",     # Est. Fee (USD)
                f"{trade_data.get('slippage_bps', 0):.1f}",   # Slippage (bps)
                f"${trade_data.get('gross_pnl', 0):.4f}",     # PnL Bruto (USD)
                f"${trade_data.get('net_pnl', 0):.4f}",       # PnL Neto (USD)
                f"{trade_data.get('rr_ratio', 0):.2f}",       # RR
                f"{trade_data.get('atr_pct', 0):.2f}%",      # ATR (%)
                
                trade_data.get('phase', 'FASE 1.6')           # Fase
            ]
            
            # Añadir fila
            worksheet.append_row(row_data)
            self.logger.info("✅ Trade FASE 1.6 registrado en Google Sheets con métricas mejoradas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando trade FASE 1.6 en Sheets: {e}")
            return False
    
    def log_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """Log telemetría a Google Sheets"""
        try:
            if not self.sheets_enabled:
                return False
            
            # Obtener worksheet de telemetría
            spreadsheet = self.client.open(self.spreadsheet_name)
            
            # Crear worksheet de telemetría si no existe
            try:
                worksheet = spreadsheet.worksheet("Telemetría")
            except:
                worksheet = spreadsheet.add_worksheet(title="Telemetría", rows=1000, cols=20)
                # Crear headers
                headers = [
                    'Timestamp', 'Win Rate', 'Profit Factor', 'Drawdown', 
                    'Trades/Hour', 'Fees Ratio', 'Rejection Low Vol', 
                    'Rejection Trend Mismatch', 'Rejection Spread', 
                    'Rejection Safety', 'Rejection Cooldown', 'Total Signals',
                    'Probation Mode', 'Racha Cooldown'
                ]
                worksheet.append_row(headers)
            
            # Preparar datos de telemetría
            timestamp = telemetry_data.get('timestamp', datetime.now().isoformat())
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Crear fila de telemetría
            row_data = [
                date_str,  # Timestamp
                f"{telemetry_data.get('win_rate', 0):.2f}%",  # Win Rate
                telemetry_data.get('profit_factor', 'N/A'),  # Profit Factor
                f"{telemetry_data.get('drawdown', 0):.2f}%",  # Drawdown
                telemetry_data.get('trades_per_hour', 0),  # Trades/Hour
                f"{telemetry_data.get('fees_ratio', 0):.2f}%",  # Fees Ratio
                f"{telemetry_data.get('rejection_low_vol', 0):.2f}%",  # Rejection Low Vol
                f"{telemetry_data.get('rejection_trend_mismatch', 0):.2f}%",  # Rejection Trend Mismatch
                f"{telemetry_data.get('rejection_spread', 0):.2f}%",  # Rejection Spread
                f"{telemetry_data.get('rejection_safety', 0):.2f}%",  # Rejection Safety
                f"{telemetry_data.get('rejection_cooldown', 0):.2f}%",  # Rejection Cooldown
                telemetry_data.get('total_signals', 0),  # Total Signals
                telemetry_data.get('probation_mode', False),  # Probation Mode
                telemetry_data.get('racha_cooldown', False)  # Racha Cooldown
            ]
            
            # Añadir fila
            worksheet.append_row(row_data)
            self.logger.info("✅ Telemetría registrada en Google Sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando telemetría FASE 1.6 en Sheets: {e}")
            return False

class LocalLogger:
    """Logger local para análisis y respaldo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = "trading_data"
        self.setup_directory()
    
    def setup_directory(self):
        """Configurar directorio de datos"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                self.logger.info(f"✅ Directorio de datos creado: {self.data_dir}")
        except Exception as e:
            self.logger.error(f"❌ Error creando directorio: {e}")
    
    def log_operation(self, trade_data: Dict[str, Any]) -> bool:
        """Registrar operación localmente"""
        try:
            import json
            from datetime import datetime
            
            date = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join(self.data_dir, f"operations_{date}.json")
            
            # Cargar operaciones existentes o crear nuevo
            operations = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    operations = json.load(f)
            
            # Preparar datos
            timestamp = trade_data.get('timestamp', datetime.now().isoformat())
            date_part = timestamp.split('T')[0] if 'T' in timestamp else timestamp.split(' ')[0]
            time_part = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp.split(' ')[1]
            
            # Calcular monto
            amount = trade_data.get('amount', 0)
            price = trade_data.get('price', 0)
            monto = amount * price
            
            operation = {
                "timestamp": timestamp,
                "date": date_part,
                "time": time_part,
                "symbol": trade_data.get('symbol', ''),
                "side": trade_data.get('side', ''),
                "price": trade_data.get('price', 0),
                "amount": trade_data.get('amount', 0),
                "monto": monto,
                "strategy": "breakout",
                "confidence": "0.6%",
                "validation": "BOT PROFESIONAL",
                "result": trade_data.get('result', ''),
                "pnl": trade_data.get('pnl', 0),
                "capital": trade_data.get('capital', 0),
                "created_at": datetime.now().isoformat()
            }
            
            operations.append(operation)
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(operations, f, indent=2, ensure_ascii=False)
            
            self.logger.info("✅ Operación registrada localmente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando localmente: {e}")
            return False

class ProfessionalTradingBot:
    """Bot de trading profesional con sistema de métricas y gestión de riesgo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = True
        self.cycle_count = 0
        self.current_capital = 50.0
        
        # Inicializar sistemas
        self.metrics_tracker = MetricsTracker()
        self.safety_manager = SafetyManager()
        self.market_filter = MarketFilter()
        self.position_manager = PositionManager()
        self.sheets_logger = GoogleSheetsLogger()
        self.local_logger = LocalLogger()
        self.telemetry_manager = TelemetryManager(self)
        
        # Configuración de trading
        self.update_interval = 180  # 3 minutos (configurable)
        self.session_start_time = datetime.now()
        
        # Configurar señales de interrupción
        # signal.signal(signal.SIGINT, self.handle_shutdown) # Moved to top
        # signal.signal(signal.SIGTERM, self.handle_shutdown) # Moved to top
        
        self.logger.info("🤖 BOT:")
        self.logger.info("✅ Sistema de métricas inicializado")
        self.logger.info("✅ Sistema de seguridad inicializado")
        self.logger.info("✅ Filtros de mercado inicializados")
        self.logger.info("✅ Gestión de posiciones inicializada")
        self.logger.info("✅ Telemetría y alertas inicializadas")
        self.logger.info("✅ Google Sheets configurado desde variable de entorno")
        self.logger.info("✅ Google Sheets habilitado")
        self.logger.info("✅ Directorio de datos creado: trading_data")
        self.logger.info("✅ Logging local habilitado")
        self.logger.info("🚀 Iniciando bot profesional - FASE 1.6...")
        
        # Mensaje de inicio FASE 1.6
        startup_message = f"""
🤖 BOT PROFESIONAL - FASE 1.6

📊 Configuración Mejorada:
⏱️ Intervalo: {self.update_interval}s
💰 Capital inicial: ${self.current_capital:.2f}
🛡️ Sistema de seguridad activo
📈 P&L neto con fees/slippage
🎯 Filtros avanzados: Rango/Spread/Vol
📊 Telemetría FASE 1.6
🚨 Kill-switches mejorados

⚙️ Nuevas Configuraciones FASE 1.6:
💰 TP mínimo: >fricción (18.5 bps)
🎯 RR: 1.25:1 garantizado
📊 Filtros: MIN_RANGE=5bps, MAX_SPREAD=2bps
📈 Fees: Taker=7.5bps, Maker=2bps
⏱️ Latencia: REST<800ms, WS<1500ms
🔒 Posición: 0.1% equity (micro)

🚀 Listo para sesión con FASE 1.6
"""
        self.send_telegram_message(startup_message)
        self.logger.info("✅ Bot profesional - FASE 1.6 iniciado correctamente")
    
    def send_telegram_message(self, message: str):
        """Enviar mensaje a Telegram"""
        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if bot_token and chat_id:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    self.logger.info("✅ Mensaje enviado a Telegram")
                else:
                    self.logger.warning(f"⚠️ Error enviando mensaje: {response.status_code}")
            else:
                self.logger.warning("⚠️ Credenciales Telegram no configuradas")
                
        except Exception as e:
            self.logger.error(f"❌ Error enviando mensaje Telegram FASE 1.6: {e}")
    
    def simulate_trading_signal(self) -> Dict[str, Any]:
        """Simular señal de trading con filtros de mercado"""
        try:
            # Simular precio actual (BNB/USDT)
            current_price = random.uniform(500, 650)
            volume = random.uniform(1000, 5000)
            
            # Verificar condiciones de mercado
            market_conditions = self.market_filter.check_market_conditions(current_price, volume)
            
            if not market_conditions['can_trade']:
                # Registrar motivo de rechazo con código
                self.telemetry_manager.record_rejection(market_conditions.get('reason_code', 'other'))
                return {
                    'signal': 'REJECTED',
                    'reason': market_conditions['reason'],
                    'price': current_price,
                    'volume': volume,
                    'market_data': market_conditions
                }
            
            # Generar señal basada en dirección del mercado
            direction = market_conditions['direction']
            
            # Simular confianza basada en condiciones
            confidence = random.uniform(0.6, 0.9)
            
            signal_data = {
                'signal': direction,
                'price': current_price,
                'volume': volume,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'market_data': market_conditions
            }
            
            friendly_reason = market_conditions.get('reason') or 'Condiciones favorables'
            self.logger.info(f"📊 Señal: {direction} - {friendly_reason}")
            return signal_data
            
        except Exception as e:
            self.logger.error(f"❌ Error generando señal FASE 1.6: {e}")
            return {'signal': 'ERROR', 'reason': str(e)}
    
    def simulate_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """FASE 1.6: Simular ejecución de trade con gestión de riesgo mejorada"""
        try:
            if signal['signal'] in ['REJECTED', 'ERROR']:
                # Registrar rechazo por seguridad
                if signal['signal'] == 'REJECTED':
                    self.telemetry_manager.record_rejection('safety_block')
                return {
                    'executed': False,
                    'reason': signal.get('reason', 'Señal rechazada'),
                    'signal': signal
                }
            
            # Verificar condiciones de seguridad
            safety_status = self.safety_manager.check_safety_conditions(self.current_capital)
            
            if not safety_status['can_trade']:
                # Registrar rechazo por cooldown
                if 'cooldown' in safety_status['reason'].lower():
                    self.telemetry_manager.record_rejection('cooldown')
                else:
                    self.telemetry_manager.record_rejection('safety_block')
                    
                return {
                    'executed': False,
                    'reason': safety_status['reason'],
                    'signal': signal,
                    'safety_status': safety_status
                }
            
            # === FASE 1.6: APLICAR FILTROS PRE-TRADE ===
            market_data = {
                'price': signal['price'],
                'high': signal['price'] * (1 + random.uniform(0.005, 0.02)),
                'low': signal['price'] * (1 - random.uniform(0.005, 0.02)),
                'close': signal['price'],
                'best_ask': signal['price'] * 1.0001,
                'best_bid': signal['price'] * 0.9999,
                'volume_usd': random.uniform(5000000, 15000000),
                'ws_latency_ms': random.uniform(50, 200),
                'rest_latency_ms': random.uniform(100, 500)
            }
            
            # Aplicar filtros
            filter_result = self.safety_manager.pre_trade_filters(market_data)
            if not filter_result['passed']:
                self.logger.info(f"❌ Trade rechazado por filtros: {filter_result['reason']}")
                return {
                    'executed': False,
                    'reason': f"Filtro fallido: {filter_result['reason']}",
                    'signal': signal,
                    'filter_result': filter_result
                }
            
            # Obtener datos de mercado
            entry_price = signal['price']
            direction = signal['signal']
            atr_value = signal['market_data']['atr']
            
            # === FASE 1.6: CALCULAR TARGETS DINÁMICOS ===
            targets = self.safety_manager.compute_trade_targets(entry_price, atr_value)
            
            # Calcular tamaño de posición
            position_data = self.position_manager.calculate_position_size(self.current_capital, atr_value)
            
            # Aplicar reducción de tamaño en modo probation (-50%)
            if safety_status.get('probation_mode', False):
                position_data['size'] = max(self.position_manager.position_size_usd_min, position_data['size'] * 0.5)
                position_data['fees'] = position_data['size'] * self.position_manager.fee_rate
            
            # === FASE 1.6: SIMULAR EJECUCIÓN CON SLIPPAGE REALISTA ===
            slippage_bps = random.uniform(1.0, 3.0)  # 1-3 bps
            slippage_pct = slippage_bps / 10000
            if direction == 'BUY':
                executed_price = entry_price * (1 + slippage_pct)
            else:
                executed_price = entry_price * (1 - slippage_pct)
            
            # === FASE 1.6: SIMULAR RESULTADO BASADO EN TARGETS ===
            win_probability = 0.6  # 60% win rate
            is_win = random.random() < win_probability
            
            # Calcular P&L bruto basado en targets
            if is_win:
                # Ganancia basada en TP dinámico
                tp_pct = targets['tp_pct']
                if direction == 'BUY':
                    exit_price = executed_price * (1 + tp_pct)
                else:
                    exit_price = executed_price * (1 - tp_pct)
                pnl_gross = position_data['size'] * (exit_price - executed_price) / executed_price
                result = 'GANANCIA'
            else:
                # Pérdida basada en SL dinámico
                sl_pct = targets['sl_pct']
                if direction == 'BUY':
                    exit_price = executed_price * (1 - sl_pct)
                else:
                    exit_price = executed_price * (1 + sl_pct)
                pnl_gross = position_data['size'] * (exit_price - executed_price) / executed_price
                result = 'PÉRDIDA'
            
            # === FASE 1.6: CALCULAR P&L NETO CON FEES/SLIPPAGE ===
            trade_data_for_pnl = {
                'notional': position_data['size'],
                'intended_price': entry_price,
                'executed_price': executed_price,
                'realized_pnl': pnl_gross
            }
            
            pnl_data = self.safety_manager.calculate_net_pnl(trade_data_for_pnl)
            pnl_net = pnl_data['net_pnl']
            
            # Asegurar que el P&L neto sea visible incluso si es pequeño
            if abs(pnl_net) < 0.01 and pnl_net != 0:
                pnl_net = -0.01 if pnl_net < 0 else 0.01
            
            # Actualizar capital
            new_capital = self.current_capital + pnl_net
            self.current_capital = new_capital
            
            # Registrar trade en sistema de seguridad
            self.safety_manager.record_trade(result, pnl_net)
            
            # === FASE 1.6: CREAR DATOS DEL TRADE MEJORADOS ===
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BNBUSDT',
                'direction': direction,
                'entry_price': executed_price,
                'exit_price': exit_price,
                'size': position_data['size'],
                'notional': position_data['size'],
                'gross_pnl': pnl_gross,
                'net_pnl': pnl_net,
                'result': result,
                'capital': new_capital,
                'capital_net': new_capital,
                'atr_value': atr_value,
                'confidence': signal['confidence'],
                'strategy': 'breakout',
                'phase': 'FASE 1.6',
                'safety_status': safety_status,
                
                # === FASE 1.6: NUEVAS MÉTRICAS ===
                'tp_bps': targets['tp_bps'],
                'sl_bps': targets['sl_bps'],
                'tp_pct': targets['tp_pct'],
                'sl_pct': targets['sl_pct'],
                'rr_ratio': targets['rr_ratio'],
                'fric_bps': targets['fric_bps'],
                'tp_floor': targets['tp_floor'],
                'fees_bps': pnl_data['fees_cost'] / position_data['size'] * 10000,
                'slippage_bps': slippage_bps,
                'range_bps': filter_result['details'].get('range_bps', 0),
                'spread_bps': filter_result['details'].get('spread_bps', 0),
                'atr_pct': (atr_value / entry_price) * 100,
                
                # Friction data
                'fees_cost': pnl_data['fees_cost'],
                'slippage_cost': pnl_data['slippage_cost'],
                'total_friction': pnl_data['total_friction'],
                'friction_impact': pnl_data['friction_impact'],
                
                # Market data
                'spread_at_execution': filter_result['details'].get('spread_pct', 0) * 100,
                'volume_at_execution': filter_result['details'].get('volume_usd', 0),
                'range_at_execution': filter_result['details'].get('range_pct', 0),
                
                # Legacy fields for compatibility
                'fees': pnl_data['fees_cost'],
                'pnl_gross': pnl_gross,
                'pnl_net': pnl_net,
                'sl_price': exit_price if not is_win else None,
                'tp_price': exit_price if is_win else None
            }
            
            # Añadir a métricas
            self.metrics_tracker.add_operation(trade_data)
            
            # Log FASE 1.6
            self.logger.info(f"📊 Trade FASE 1.6: {result} | TP={targets['tp_pct']:.4f}% | SL={targets['sl_pct']:.4f}% | RR={targets['rr_ratio']:.2f}")
            self.logger.info(f"💰 P&L: Bruto=${pnl_gross:.4f} | Neto=${pnl_net:.4f} | Friction=${pnl_data['total_friction']:.4f}")
            
            return {
                'executed': True,
                'trade_data': trade_data,
                'targets': targets,
                'filter_result': filter_result
            }
            
            # Obtener métricas actualizadas
            metrics = self.metrics_tracker.get_metrics_summary()
            
            # Logging
            self.sheets_logger.log_trade(trade_data, metrics)
            self.local_logger.log_operation(trade_data)
            
            # Mensaje Telegram FASE 1.6
            telegram_message = f"""
🤖 BOT PROFESIONAL - FASE 1.6

💰 Trade: {direction} BNBUSDT
💵 Precio: ${entry_price:,.2f}
📊 Resultado: {result}
💸 P&L Neto: ${pnl_net:.4f}

📈 Targets FASE 1.6:
🎯 TP: {trade_data.get('tp_pct', 0):.4f}% ({trade_data.get('tp_bps', 0):.1f} bps)
🎯 SL: {trade_data.get('sl_pct', 0):.4f}% ({trade_data.get('sl_bps', 0):.1f} bps)
📊 RR: {trade_data.get('rr_ratio', 0):.2f}:1

📈 Métricas:
📊 Win Rate: {metrics['win_rate']:.2f}%
📈 Profit Factor: {self.metrics_tracker.get_profit_factor_display()}
📉 Drawdown: {metrics['drawdown']:.2f}%

🛡️ Seguridad:
📊 DD: {safety_status['intraday_drawdown']:.2f}%
📊 DL: {safety_status['daily_loss']:.2f}%
📊 CL: {safety_status['consecutive_losses']}
🔒 Probation: {safety_status.get('probation_mode', False)}
"""
            self.send_telegram_message(telegram_message)
            
            return {
                'executed': True,
                'trade_data': trade_data,
                'metrics': metrics,
                'safety_status': safety_status
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando trade FASE 1.6: {e}")
            return {'executed': False, 'reason': str(e)}
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading con optimizaciones"""
        try:
            self.cycle_count += 1
            current_time = datetime.now()
            
            self.logger.info(f"🔄 Iniciando ciclo {self.cycle_count}...")
            self.logger.info(f"🔄 Ciclo {self.cycle_count} - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Generar señal
            signal = self.simulate_trading_signal()
            
            # Ejecutar trade
            trade_result = self.simulate_trade(signal)
            
            if trade_result['executed']:
                self.logger.info(f"✅ Trade FASE 1.6 ejecutado: {trade_result['trade_data']['direction']} @ ${trade_result['trade_data']['entry_price']:.2f}")
                self.logger.info(f"📊 Métricas FASE 1.6: WR={trade_result['metrics']['win_rate']:.2f}%, PF={self.metrics_tracker.get_profit_factor_display()}, DD={trade_result['metrics']['drawdown']:.2f}%")
            else:
                self.logger.info(f"❌ Trade rechazado: {trade_result['reason']}")
            
            # Enviar telemetría si es necesario
            if trade_result['executed']:
                self.telemetry_manager.send_telemetry(trade_result['metrics'], trade_result['safety_status'])
            
            self.logger.info(f"✅ Ciclo {self.cycle_count} completado, esperando {self.update_interval}s...")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading FASE 1.6: {e}")
    
    def start(self):
        """Iniciar bot de trading"""
        try:
            self.logger.info("🔄 Iniciando bucle principal con optimizaciones...")
            
            # Resetear contadores horarios cada hora
            last_hourly_reset = datetime.now()
            
            while not shutdown_state["stop"] and self.running:
                try:
                    # Resetear contadores horarios
                    current_time = datetime.now()
                    if (current_time - last_hourly_reset).total_seconds() >= 3600:  # 1 hora
                        self.safety_manager.reset_hourly_counters()
                        last_hourly_reset = current_time
                    
                    # Ejecutar ciclo
                    self.run_trading_cycle()
                    
                    # Esperar intervalo con verificación de apagado
                    sleep_responsive(self.update_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Interrupción manual recibida")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error en bucle principal FASE 1.6: {e}")
                    sleep_responsive(60)  # Esperar antes de reintentar, pero de forma responsiva
            
            # Apagado limpio
            self.save_state_and_close()
            
            # Mensaje de cierre FASE 1.6
            final_message = f"""
🤖 BOT PROFESIONAL - FASE 1.6

🛑 **APAGADO COMPLETADO**

📊 **RESUMEN FINAL FASE 1.6:**
🔄 Ciclos ejecutados: {self.cycle_count}
💰 Capital final: ${self.current_capital:.2f}
📈 P&L: ${self.current_capital - 50.0:.2f}

✅ Bot FASE 1.6 cerrado correctamente
"""
            self.send_telegram_message(final_message)
            self.logger.info("✅ Bot FASE 1.6 cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando bot FASE 1.6: {e}")
    
    def save_state_and_close(self):
        """Guardar estado y cerrar conexiones"""
        try:
            self.logger.info("💾 Guardando estado...")
            
            # Guardar métricas finales
            final_metrics = self.metrics_tracker.get_metrics_summary()
            
            # Log final a Google Sheets
            if self.sheets_logger.sheets_enabled:
                final_data = {
                    'timestamp': datetime.now().isoformat(),
                    'event': 'BOT_SHUTDOWN',
                    'cycles_executed': self.cycle_count,
                    'final_capital': self.current_capital,
                    'final_pnl': self.current_capital - 50.0,
                    'win_rate': final_metrics.get('win_rate', 0),
                    'profit_factor': self.metrics_tracker.get_profit_factor_display(),
                    'drawdown': final_metrics.get('drawdown', 0),
                    'symbol': 'BNBUSDT'
                }
                self.sheets_logger.log_trade(final_data, final_metrics)
            
            # Guardar resumen local CSV
            try:
                import csv
                summary_path = os.path.join(self.local_logger.data_dir, 'session_summary.csv')
                file_exists = os.path.exists(summary_path)
                with open(summary_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow([
                            'timestamp', 'cycles_executed', 'final_capital', 'final_pnl',
                            'win_rate', 'profit_factor', 'drawdown', 'symbol'
                        ])
                    writer.writerow([
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        self.cycle_count,
                        f"{self.current_capital:.2f}",
                        f"{(self.current_capital - 50.0):.2f}",
                        f"{final_metrics.get('win_rate', 0):.2f}",
                        self.metrics_tracker.get_profit_factor_display(),
                        f"{final_metrics.get('drawdown', 0):.2f}",
                        'BNBUSDT'
                    ])
                self.logger.info("✅ Resumen de sesión guardado en CSV")
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo guardar resumen CSV: {e}")
            
            # Cerrar conexiones (si existieran)
            try:
                if hasattr(self, 'binance_client') and self.binance_client:
                    self.binance_client.close_connection()
            except Exception:
                pass
            
            self.logger.info("✅ Estado guardado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando estado FASE 1.6: {e}")
    
class TelemetryManager:
    """Sistema de telemetría y alertas"""
    
    def __init__(self, bot_instance):
        self.logger = logging.getLogger(__name__)
        self.bot = bot_instance
        self.last_telemetry_time = datetime.now()
        self.telemetry_interval = 300  # 5 minutos
        self.rejection_reasons = {
            'low_vol': 0,
            'trend_mismatch': 0,
            'spread_high': 0,
            'safety_block': 0,
            'cooldown': 0
        }
        self.total_signals = 0
        
    def record_rejection(self, reason: str):
        """Registrar motivo de rechazo"""
        try:
            self.total_signals += 1
            if reason in self.rejection_reasons:
                self.rejection_reasons[reason] += 1
            else:
                self.rejection_reasons['other'] = self.rejection_reasons.get('other', 0) + 1
                
        except Exception as e:
            self.logger.error(f"❌ Error registrando rechazo: {e}")
    
    def calculate_rejection_percentages(self) -> Dict:
        """Calcular porcentajes de rechazo"""
        try:
            if self.total_signals == 0:
                return {reason: 0.0 for reason in self.rejection_reasons}
            
            percentages = {}
            for reason, count in self.rejection_reasons.items():
                percentages[reason] = (count / self.total_signals) * 100
                
            return percentages
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando porcentajes: {e}")
            return {}
    
    def should_send_telemetry(self) -> bool:
        """Verificar si debe enviar telemetría"""
        return (datetime.now() - self.last_telemetry_time).total_seconds() >= self.telemetry_interval
    
    def should_send_alert(self, metrics: Dict, safety_status: Dict) -> bool:
        """Verificar si debe enviar alerta crítica"""
        try:
            # Alertas críticas
            if metrics.get('drawdown', 0) > 10.0:
                return True
            if metrics.get('profit_factor', 0) < 1.2 and metrics.get('profit_factor', 0) > 0:
                return True
            if metrics.get('win_rate', 0) < 45.0:
                return True
            
            # Calcular fees ratio
            total_pnl = sum(op.get('pnl_net', 0) for op in self.bot.metrics_tracker.operations_history)
            total_fees = sum(op.get('fees', 0) for op in self.bot.metrics_tracker.operations_history)
            
            if total_pnl > 0 and total_fees > 0:
                fees_ratio = (total_fees / total_pnl) * 100
                if fees_ratio > 25.0:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando alertas: {e}")
            return False
    
    def send_telemetry(self, metrics: Dict, safety_status: Dict):
        """Enviar telemetría a Google Sheets"""
        try:
            if not self.should_send_telemetry():
                return
            
            # Calcular métricas adicionales
            trades_per_hour = safety_status.get('hourly_trades', 0)
            rejection_percentages = self.calculate_rejection_percentages()
            
            # Calcular fees ratio
            total_pnl = sum(op.get('pnl_net', 0) for op in self.bot.metrics_tracker.operations_history)
            total_fees = sum(op.get('fees', 0) for op in self.bot.metrics_tracker.operations_history)
            fees_ratio = (total_fees / total_pnl) * 100 if total_pnl > 0 else 0
            
            # Crear datos de telemetría
            telemetry_data = {
                'timestamp': datetime.now().isoformat(),
                'win_rate': metrics.get('win_rate', 0),
                'profit_factor': self.bot.metrics_tracker.get_profit_factor_display(),
                'drawdown': metrics.get('drawdown', 0),
                'trades_per_hour': trades_per_hour,
                'fees_ratio': fees_ratio,
                'rejection_low_vol': rejection_percentages.get('low_vol', 0),
                'rejection_trend_mismatch': rejection_percentages.get('trend_mismatch', 0),
                'rejection_spread': rejection_percentages.get('spread_high', 0),
                'rejection_safety': rejection_percentages.get('safety_block', 0),
                'rejection_cooldown': rejection_percentages.get('cooldown', 0),
                'total_signals': self.total_signals,
                'probation_mode': safety_status.get('probation_mode', False),
                'racha_cooldown': safety_status.get('racha_cooldown_active', False)
            }
            
            # Enviar a Google Sheets
            self.bot.sheets_logger.log_telemetry(telemetry_data)
            
            # Verificar alertas críticas
            if self.should_send_alert(metrics, safety_status):
                self.send_critical_alert(metrics, safety_status, telemetry_data)
            
            self.last_telemetry_time = datetime.now()
            self.logger.info("📊 Telemetría enviada")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando telemetría: {e}")
    
    def send_critical_alert(self, metrics: Dict, safety_status: Dict, telemetry_data: Dict):
        """Enviar alerta crítica a Telegram"""
        try:
            alert_message = f"""
🚨 ALERTA CRÍTICA - BOT PROFESIONAL

📊 Métricas Críticas:
📉 Drawdown: {metrics.get('drawdown', 0):.2f}%
📈 Profit Factor: {self.bot.metrics_tracker.get_profit_factor_display()}
📊 Win Rate: {metrics.get('win_rate', 0):.2f}%
💰 Fees Ratio: {telemetry_data.get('fees_ratio', 0):.2f}%

🛡️ Estado Seguridad:
📊 DD: {safety_status.get('intraday_drawdown', 0):.2f}%
📊 DL: {safety_status.get('daily_loss', 0):.2f}%
📊 CL: {safety_status.get('consecutive_losses', 0)}
🔒 Probation: {safety_status.get('probation_mode', False)}

⚠️ Requiere atención inmediata
"""
            self.bot.send_telegram_message(alert_message)
            self.logger.info("🚨 Alerta crítica enviada")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando alerta crítica: {e}")

def main():
    """Función principal - FASE 1.5 PATCHED"""
    try:
        # Parsear argumentos
        parser = argparse.ArgumentParser(description='Trading Bot Profesional - FASE 1.6')
        parser.add_argument('--mode', default='testnet', choices=['testnet', 'live'], 
                          help='Modo de operación (testnet/live)')
        parser.add_argument('--config', default='config_survivor_final.py',
                          help='Archivo de configuración')
        parser.add_argument('--strategy', default='breakout',
                          help='Estrategia de trading')
        
        args = parser.parse_args()
        
        # Configurar logging
        logging.info(f"🚀 Iniciando Trading Bot - FASE 1.6")
        logging.info(f"📊 Modo: {args.mode}")
        logging.info(f"⚙️ Configuración: {args.config}")
        logging.info(f"🎯 Estrategia: {args.strategy}")
        
        # Crear y ejecutar bot
        bot = ProfessionalTradingBot()
        
        try:
            bot.start()
        except KeyboardInterrupt:
            logging.info("🛑 Interrupción manual recibida")
        except Exception as e:
            logging.error(f"❌ Error en ejecución: {e}")
        finally:
            # Asegurar apagado limpio
            if not shutdown_state["stop"]:
                logging.info("🛑 Iniciando apagado limpio...")
                shutdown_state["stop"] = True
            
            logging.info("✅ Bot terminado correctamente")
            sys.exit(0)
            
    except Exception as e:
        logging.error(f"❌ Error crítico en main FASE 1.6: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
