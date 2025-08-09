#!/usr/bin/env python3
"""
🎯 AUTO PAIR SELECTOR - FASE 1.6
Módulo para seleccionar automáticamente los mejores pares en tendencia
"""

import os
import time
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoPairSelector:
    """Selector automático de pares basado en métricas de mercado"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # === CONFIGURACIÓN AUTO PAIR SELECTOR ===
        self.auto_pair_selector = os.getenv('AUTO_PAIR_SELECTOR', 'false').lower() == 'true'
        self.pairs_candidates = os.getenv('PAIRS_CANDIDATES', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,TONUSDT,MATICUSDT,ARBUSDT,OPUSDT,LTCUSDT,APTUSDT,TRXUSDT').split(',')
        self.max_active_pairs = int(os.getenv('MAX_ACTIVE_PAIRS', '4'))
        self.rebalance_minutes = int(os.getenv('REBALANCE_MINUTES', '60'))
        self.lookback_hours = int(os.getenv('LOOKBACK_HOURS', '24'))
        
        # === AUTO PAIR SELECTOR: FILTROS MÍNIMOS ===
        self.cand_min_24h_volume_usd = float(os.getenv('CAND_MIN_24H_VOLUME_USD', '100000000'))  # 100M USD
        self.cand_min_atr_bps = float(os.getenv('CAND_MIN_ATR_BPS', '12.0'))  # 0.12% (REDUCIDO de 15.0)
        self.cand_max_spread_bps = float(os.getenv('CAND_MAX_SPREAD_BPS', '2.0'))  # 0.02%
        self.cand_min_trend_score = float(os.getenv('CAND_MIN_TREND_SCORE', '0.60'))  # 0.6
        self.cand_max_correlation = float(os.getenv('CAND_MAX_CORRELATION', '0.85'))  # 0.85
        
        # === SEGURIDAD DE CAMBIO ===
        self.do_not_switch_if_position_open = os.getenv('DO_NOT_SWITCH_IF_POSITION_OPEN', 'true').lower() == 'true'
        self.min_hours_between_switches = int(os.getenv('MIN_HOURS_BETWEEN_SWITCHES', '2'))
        
        # === FALLBACK ===
        self.enable_multi_pair = os.getenv('ENABLE_MULTI_PAIR', 'true').lower() == 'true'
        self.fallback_pairs = os.getenv('PAIRS', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT').split(',')
        
        # === ESTADO INTERNO ===
        self.last_rebalance = None
        self.active_pairs = []
        self.pair_scores = {}
        self.pair_metrics = {}
        
        self.logger.info(f"🎯 Auto Pair Selector inicializado:")
        self.logger.info(f"📊 Candidatos: {len(self.pairs_candidates)} pares")
        self.logger.info(f"🎯 Máximo activos: {self.max_active_pairs}")
        self.logger.info(f"🔄 Rebalance: {self.rebalance_minutes} min")
        self.logger.info(f"📈 Lookback: {self.lookback_hours} horas")
    
    def get_market_data(self, symbol: str, interval: str = '1h', limit: int = 24) -> Optional[pd.DataFrame]:
        """Obtener datos de mercado para un símbolo"""
        try:
            # Simular datos de mercado para testing
            if self.config.MODE == 'testnet':
                return self._simulate_market_data(symbol, interval, limit)
            
            # TODO: Implementar llamada real a Binance API
            # Por ahora, usar simulación
            return self._simulate_market_data(symbol, interval, limit)
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos para {symbol}: {e}")
            return None
    
    def _simulate_market_data(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Simular datos de mercado para testing"""
        try:
            # Precios base por símbolo
            base_prices = {
                'BTCUSDT': 45000,
                'ETHUSDT': 2800,
                'BNBUSDT': 600,
                'SOLUSDT': 100,
                'XRPUSDT': 0.5,
                'ADAUSDT': 0.4,
                'DOGEUSDT': 0.08,
                'LINKUSDT': 15,
                'TONUSDT': 2.5,
                'MATICUSDT': 0.8,
                'ARBUSDT': 1.2,
                'OPUSDT': 2.8,
                'LTCUSDT': 70,
                'APTUSDT': 8,
                'TRXUSDT': 0.08
            }
            
            base_price = base_prices.get(symbol, 100)
            
            # Generar datos simulados
            dates = pd.date_range(end=datetime.now(), periods=limit, freq='H')
            np.random.seed(hash(symbol) % 1000)  # Seed consistente por símbolo
            
            # Simular OHLCV
            prices = []
            for i in range(limit):
                # Simular movimiento de precio
                change_pct = np.random.normal(0, 0.02)  # 2% std dev
                price = base_price * (1 + change_pct)
                
                # Simular OHLC
                high = price * (1 + abs(np.random.normal(0, 0.01)))
                low = price * (1 - abs(np.random.normal(0, 0.01)))
                open_price = price * (1 + np.random.normal(0, 0.005))
                close_price = price
                
                # Simular volumen
                volume = np.random.uniform(1000000, 50000000)  # 1M-50M USD
                
                prices.append({
                    'timestamp': dates[i],
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close_price,
                    'volume': volume
                })
            
            return pd.DataFrame(prices)
            
        except Exception as e:
            self.logger.error(f"❌ Error simulando datos para {symbol}: {e}")
            return None
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calcular ATR (Average True Range)"""
        try:
            if len(df) < period:
                return 0.0
            
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            tr1 = high - low
            tr2 = np.abs(high - np.roll(close, 1))
            tr3 = np.abs(low - np.roll(close, 1))
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = np.mean(tr[-period:])
            
            return atr
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando ATR: {e}")
            return 0.0
    
    def calculate_trend_score(self, df: pd.DataFrame) -> float:
        """Calcular score de tendencia (0-1)"""
        try:
            if len(df) < 20:
                return 0.5
            
            close = df['close'].values
            
            # EMA 20, 50, 100
            ema20 = np.mean(close[-20:])
            ema50 = np.mean(close[-50:]) if len(close) >= 50 else np.mean(close)
            ema100 = np.mean(close[-100:]) if len(close) >= 100 else np.mean(close)
            
            # Score basado en alineación de EMAs
            score = 0.0
            
            # Alineación alcista: EMA20 > EMA50 > EMA100
            if ema20 > ema50 > ema100:
                score += 0.4
            # Alineación bajista: EMA20 < EMA50 < EMA100
            elif ema20 < ema50 < ema100:
                score += 0.4
            
            # Pendiente de regresión lineal (4h)
            if len(close) >= 4:
                x = np.arange(len(close[-4:]))
                y = close[-4:]
                slope = np.polyfit(x, y, 1)[0]
                
                # Normalizar pendiente
                slope_norm = min(abs(slope) / close[-1] * 100, 1.0)
                score += slope_norm * 0.3
            
            # Bonus por volatilidad (ADX simulado)
            atr = self.calculate_atr(df, 14)
            atr_pct = (atr / close[-1]) * 100
            if atr_pct > 0.5:  # > 0.5% ATR
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando trend score: {e}")
            return 0.5
    
    def calculate_correlation(self, df1: pd.DataFrame, df2: pd.DataFrame) -> float:
        """Calcular correlación entre dos pares"""
        try:
            if len(df1) < 4 or len(df2) < 4:
                return 0.0
            
            # Usar últimos 4 períodos
            returns1 = df1['close'].pct_change().dropna().tail(4)
            returns2 = df2['close'].pct_change().dropna().tail(4)
            
            if len(returns1) != len(returns2):
                return 0.0
            
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            return abs(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando correlación: {e}")
            return 0.0
    
    def calculate_pair_score(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular score completo para un par"""
        try:
            if df is None or len(df) == 0:
                return {'score': 0.0, 'metrics': {}}
            
            # Métricas básicas
            close_price = df['close'].iloc[-1]
            volume_24h = df['volume'].sum()
            atr = self.calculate_atr(df, 14)
            atr_bps = (atr / close_price) * 100 * 100  # Convertir a bps
            
            # Rango
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            range_bps = ((high_24h - low_24h) / close_price) * 100 * 100
            
            # Spread simulado
            spread_bps = np.random.uniform(0.5, 2.0)  # 0.5-2.0 bps
            
            # Trend score
            trend_score = self.calculate_trend_score(df)
            
            # Volumen rank (simulado)
            volume_rank = np.random.uniform(0.3, 1.0)  # 0.3-1.0
            
            # Normalización
            def normalize(value, min_val, max_val):
                if max_val == min_val:
                    return 0.5
                return (value - min_val) / (max_val - min_val)
            
            # Score calculation
            score = (
                0.35 * volume_rank +
                0.25 * normalize(atr_bps, 10, 50) +
                0.25 * trend_score +
                0.10 * normalize(range_bps, 20, 200) -
                0.15 * normalize(spread_bps, 0.5, 3.0)
            )
            
            # Aplicar filtros mínimos
            if volume_24h < self.cand_min_24h_volume_usd:
                score = 0.0
            if atr_bps < self.cand_min_atr_bps:
                score = 0.0
            if spread_bps > self.cand_max_spread_bps:
                score = 0.0
            if trend_score < self.cand_min_trend_score:
                score = 0.0
            
            metrics = {
                'volume_24h': volume_24h,
                'atr_bps': atr_bps,
                'range_bps': range_bps,
                'spread_bps': spread_bps,
                'trend_score': trend_score,
                'volume_rank': volume_rank,
                'close_price': close_price
            }
            
            return {'score': max(score, 0.0), 'metrics': metrics}
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando score para {symbol}: {e}")
            return {'score': 0.0, 'metrics': {}}
    
    def select_active_pairs(self, current_positions: List[str] = None) -> List[str]:
        """Seleccionar pares activos basado en métricas"""
        try:
            if not self.auto_pair_selector:
                self.logger.info("🎯 Auto Pair Selector desactivado, usando pares por defecto")
                return self.fallback_pairs[:self.max_active_pairs]
            
            self.logger.info(f"🎯 Iniciando selección de pares activos...")
            self.logger.info(f"📊 Candidatos: {len(self.pairs_candidates)} pares")
            
            # Obtener datos para todos los candidatos
            pair_data = {}
            for symbol in self.pairs_candidates:
                df = self.get_market_data(symbol, '1h', self.lookback_hours)
                if df is not None:
                    pair_data[symbol] = df
            
            if not pair_data:
                self.logger.warning("⚠️ No se pudieron obtener datos, usando fallback")
                return self.fallback_pairs[:self.max_active_pairs]
            
            # Calcular scores
            pair_scores = {}
            for symbol, df in pair_data.items():
                result = self.calculate_pair_score(symbol, df)
                pair_scores[symbol] = result
                self.pair_metrics[symbol] = result['metrics']
            
            # Ordenar por score
            sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            
            # Seleccionar top pares
            selected_pairs = []
            for symbol, score_data in sorted_pairs:
                if len(selected_pairs) >= self.max_active_pairs:
                    break
                
                # Verificar si hay posición abierta
                if current_positions and symbol in current_positions:
                    if self.do_not_switch_if_position_open:
                        self.logger.info(f"🛡️ Manteniendo {symbol} (posición abierta)")
                        selected_pairs.append(symbol)
                        continue
                
                # Verificar correlación con pares ya seleccionados
                correlation_ok = True
                for selected_pair in selected_pairs:
                    if selected_pair in pair_data:
                        corr = self.calculate_correlation(pair_data[symbol], pair_data[selected_pair])
                        if corr > self.cand_max_correlation:
                            self.logger.info(f"📊 {symbol} descartado por correlación alta ({corr:.2f}) con {selected_pair}")
                            correlation_ok = False
                            break
                
                if correlation_ok and score_data['score'] > 0:
                    selected_pairs.append(symbol)
                    self.logger.info(f"✅ {symbol} seleccionado (score: {score_data['score']:.3f})")
            
            # Fallback si no hay suficientes pares
            if len(selected_pairs) < self.max_active_pairs:
                self.logger.warning(f"⚠️ Solo {len(selected_pairs)} pares seleccionados, añadiendo fallback")
                for symbol in self.fallback_pairs:
                    if symbol not in selected_pairs and len(selected_pairs) < self.max_active_pairs:
                        selected_pairs.append(symbol)
            
            self.active_pairs = selected_pairs
            self.pair_scores = {k: v['score'] for k, v in pair_scores.items()}
            self.last_rebalance = datetime.now()
            
            self.logger.info(f"🎯 Pares activos seleccionados: {', '.join(selected_pairs)}")
            return selected_pairs
            
        except Exception as e:
            self.logger.error(f"❌ Error en selección de pares: {e}")
            return self.fallback_pairs[:self.max_active_pairs]
    
    def should_rebalance(self, current_positions: List[str] = None) -> bool:
        """Verificar si se debe rebalancear"""
        try:
            if not self.auto_pair_selector:
                return False
            
            # Verificar tiempo desde último rebalance
            if self.last_rebalance is None:
                return True
            
            time_since_rebalance = datetime.now() - self.last_rebalance
            if time_since_rebalance.total_seconds() < self.rebalance_minutes * 60:
                return False
            
            # Verificar si hay posiciones abiertas
            if current_positions and self.do_not_switch_if_position_open:
                if any(pos in self.active_pairs for pos in current_positions):
                    self.logger.info("🛡️ No rebalanceando (posiciones abiertas)")
                    return False
            
            # Verificar tiempo mínimo entre switches
            if self.last_rebalance and time_since_rebalance.total_seconds() < self.min_hours_between_switches * 3600:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando rebalance: {e}")
            return False
    
    def rebalance_pairs(self) -> bool:
        """Rebalancear pares activos"""
        try:
            if not self.auto_pair_selector:
                return False
            
            self.logger.info("🔄 Iniciando rebalance de pares...")
            new_active_pairs = self.select_active_pairs()
            
            if new_active_pairs and new_active_pairs != self.active_pairs:
                old_pairs = ', '.join(self.active_pairs)
                self.active_pairs = new_active_pairs
                new_pairs = ', '.join(self.active_pairs)
                
                self.logger.info(f"🔄 Pares rebalanceados: {old_pairs} → {new_pairs}")
                self.last_rebalance = datetime.now()
                return True
            else:
                self.logger.info("📊 No se requirió rebalance (pares sin cambios)")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error rebalanceando pares: {e}")
            return False
    
    def get_universe_data(self) -> Dict[str, Any]:
        """Obtener datos del universo para telemetría"""
        try:
            universe_data = []
            
            for symbol in self.pairs_candidates:
                if symbol in self.pair_metrics:
                    metrics = self.pair_metrics[symbol]
                    score = self.pair_scores.get(symbol, 0.0)
                    
                    universe_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'pair': symbol,
                        'score': score,
                        'vol_usd_24h': metrics.get('volume_24h', 0),
                        'atr_bps': metrics.get('atr_bps', 0),
                        'range_bps': metrics.get('range_bps', 0),
                        'spread_bps': metrics.get('spread_bps', 0),
                        'trend_score': metrics.get('trend_score', 0),
                        'corr_max': 0.0,  # TODO: calcular correlación máxima
                        'active': symbol in self.active_pairs
                    })
            
            return {
                'universe_data': universe_data,
                'active_pairs': self.active_pairs,
                'last_rebalance': self.last_rebalance.isoformat() if self.last_rebalance else None,
                'next_rebalance': (self.last_rebalance + timedelta(minutes=self.rebalance_minutes)).isoformat() if self.last_rebalance else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos del universo: {e}")
            return {}
    
    def log_universe_summary(self):
        """Loggear resumen del universo"""
        try:
            if not self.pair_scores:
                return
            
            self.logger.info("📊 RESUMEN DEL UNIVERSO:")
            self.logger.info("=" * 50)
            
            # Top 5 candidatos
            sorted_scores = sorted(self.pair_scores.items(), key=lambda x: x[1], reverse=True)
            self.logger.info("🏆 TOP 5 CANDIDATOS:")
            
            for i, (symbol, score) in enumerate(sorted_scores[:5], 1):
                metrics = self.pair_metrics.get(symbol, {})
                status = "✅ ACTIVO" if symbol in self.active_pairs else "⏳ CANDIDATO"
                
                self.logger.info(f"{i}. {symbol}: {score:.3f} | "
                               f"Vol: ${metrics.get('volume_24h', 0)/1e6:.1f}M | "
                               f"ATR: {metrics.get('atr_bps', 0):.1f}bps | "
                               f"Trend: {metrics.get('trend_score', 0):.2f} | "
                               f"{status}")
            
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"❌ Error loggeando resumen del universo: {e}")

# Instancia global
pair_selector = None

def init_pair_selector(config):
    """Inicializar selector de pares"""
    global pair_selector
    pair_selector = AutoPairSelector(config)
    return pair_selector

def get_pair_selector():
    """Obtener instancia del selector de pares"""
    return pair_selector
