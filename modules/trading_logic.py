"""
🎯 LÓGICA DE TRADING MEJORADA
Estrategias de trading con validación y gestión de riesgo
"""

# import pandas as pd  # Removido para compatibilidad con plan gratuito
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from modules.config import TradingConfig

class TradingLogic:
    """Lógica de trading con estrategias mejoradas"""
    
    def __init__(self, strategy: str = 'breakout'):
        """
        Inicializar lógica de trading
        
        Args:
            strategy: Estrategia a usar (breakout, scalping)
        """
        self.strategy = strategy
        self.config = TradingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Historial de operaciones
        self.trade_history = []
        self.daily_pnl = 0.0
        
    def analyze_breakout_strategy(self, historical_data: List[Dict]) -> Dict:
        """
        Analizar estrategia de breakout mejorada
        
        Args:
            historical_data: Datos históricos
            
        Returns:
            Señal de trading con análisis completo
        """
        if len(historical_data) < 20:
            return self._create_wait_signal("Datos insuficientes para breakout")
        
        # Extraer datos
        prices = [float(candle['close']) for candle in historical_data]
        volumes = [float(candle['volume']) for candle in historical_data]
        current_price = prices[-1]
        
        # Calcular niveles técnicos
        lookback = self.config.STRATEGIES['breakout']['lookback_period']
        recent_prices = prices[-lookback:]
        
        support = min(recent_prices)
        resistance = max(recent_prices)
        
        # Calcular indicadores adicionales
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
        
        # Análisis de volumen
        avg_volume = np.mean(volumes[-10:])
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume
        
        # Detectar breakout
        breakout_threshold = self.config.STRATEGIES['breakout']['breakout_threshold']
        
        # Breakout de resistencia (señal de compra)
        if current_price > resistance * (1 + breakout_threshold):
            signal = "BUY"
            reason = f"Breakout de resistencia: ${resistance:,.2f} → ${current_price:,.2f}"
            confidence = self._calculate_confidence(
                price_strength=1.0,
                volume_confirmation=bool(volume_ratio > 1.5),
                trend_alignment=bool(current_price > sma_20 and sma_20 > sma_50)
            )
        elif current_price < support * (1 - breakout_threshold):
            signal = "SELL"
            reason = f"Breakout de soporte: ${support:,.2f} → ${current_price:,.2f}"
            confidence = self._calculate_confidence(
                price_strength=1.0,
                volume_confirmation=bool(volume_ratio > 1.5),
                trend_alignment=bool(current_price < sma_20 and sma_20 < sma_50)
            )
        elif (resistance - current_price) / resistance < 0.01:
            signal = "SELL"
            reason = f"Acercamiento a resistencia: ${current_price:,.2f} → ${resistance:,.2f}"
            confidence = self._calculate_confidence(
                price_strength=0.5,
                volume_confirmation=bool(volume_ratio > 1.2),
                trend_alignment=bool(current_price < sma_20)
            )
        elif (current_price - support) / support < 0.01:
            signal = "BUY"
            reason = f"Acercamiento a soporte: ${current_price:,.2f} → ${support:,.2f}"
            confidence = self._calculate_confidence(
                price_strength=0.5,
                volume_confirmation=bool(volume_ratio > 1.2),
                trend_alignment=bool(current_price > sma_20)
            )
        else:
            return self._create_wait_signal("Precio en rango, esperando breakout")
        
        # Crear señal completa
        return {
            'signal': signal,
            'reason': reason,
            'confidence': confidence,
            'current_price': current_price,
            'resistance': resistance,
            'support': support,
            'volume_ratio': volume_ratio,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'timestamp': datetime.now().isoformat(),
            'strategy': 'breakout'
        }
    
    def analyze_scalping_strategy(self, historical_data: List[Dict]) -> Dict:
        """
        Analizar estrategia de scalping mejorada
        
        Args:
            historical_data: Datos históricos (últimos 30 minutos)
            
        Returns:
            Señal de trading con análisis completo
        """
        if len(historical_data) < 10:
            return self._create_wait_signal("Datos insuficientes para scalping")
        
        # Extraer datos recientes
        prices = [float(candle['close']) for candle in historical_data[-10:]]
        volumes = [float(candle['volume']) for candle in historical_data[-10:]]
        current_price = prices[-1]
        
        # Calcular cambios de precio
        price_changes = []
        for i in range(1, len(prices)):
            change = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
            price_changes.append(change)
        
        avg_change = np.mean(price_changes)
        volatility = np.std(price_changes)
        
        # Análisis de momentum
        momentum = (current_price - prices[0]) / prices[0] * 100
        
        # Análisis de volumen
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume
        
        # Detectar señales de scalping
        buy_threshold = self.config.STRATEGIES['scalping']['buy_threshold']
        sell_threshold = self.config.STRATEGIES['scalping']['sell_threshold']
        
        # Señal de compra (caída)
        if avg_change < -buy_threshold and volatility < 2.0:
            signal = "BUY"
            reason = f"Caída detectada: {avg_change:.2f}% en últimos minutos"
            confidence = self._calculate_confidence(
                price_strength=min(0.8, abs(avg_change) / buy_threshold),
                volume_confirmation=bool(volume_ratio > 1.3),
                trend_alignment=bool(momentum > -1.0)
            )
        elif avg_change > sell_threshold and volatility < 2.0:
            signal = "SELL"
            reason = f"Subida detectada: {avg_change:.2f}% en últimos minutos"
            confidence = self._calculate_confidence(
                price_strength=min(0.8, avg_change / sell_threshold),
                volume_confirmation=bool(volume_ratio > 1.3),
                trend_alignment=bool(momentum < 1.0)
            )
        elif abs(avg_change) < 0.005:
            return self._create_wait_signal("Precio consolidando, esperar movimiento")
            
        else:
            return self._create_wait_signal("Sin señales claras de scalping")
        
        # Crear señal completa
        return {
            'signal': signal,
            'reason': reason,
            'confidence': confidence,
            'current_price': current_price,
            'avg_change': avg_change,
            'volatility': volatility,
            'momentum': momentum,
            'volume_ratio': volume_ratio,
            'timestamp': datetime.now().isoformat(),
            'strategy': 'scalping'
        }
    
    def _calculate_confidence(self, price_strength: float, volume_confirmation: bool, trend_alignment: bool) -> float:
        """
        Calcular confianza de la señal
        
        Args:
            price_strength: Fuerza del movimiento de precio (0-1)
            volume_confirmation: Si el volumen confirma la señal
            trend_alignment: Si está alineado con la tendencia
            
        Returns:
            Confianza calculada (0-1)
        """
        base_confidence = price_strength * 0.6  # 60% peso al precio
        
        if volume_confirmation:
            base_confidence += 0.2  # 20% bonus por volumen
        
        if trend_alignment:
            base_confidence += 0.2  # 20% bonus por tendencia
        
        return min(0.95, base_confidence)  # Máximo 95%
    
    def _create_wait_signal(self, reason: str) -> Dict:
        """Crear señal de espera"""
        return {
            'signal': 'WAIT',
            'reason': reason,
            'confidence': 0.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def should_execute_trade(self, signal: Dict) -> bool:
        """
        Determinar si debe ejecutar la operación
        
        Args:
            signal: Señal de trading
            
        Returns:
            True si debe ejecutar
        """
        if signal['signal'] == 'WAIT':
            return False
        
        # Verificar umbral de confianza
        confidence_threshold = self.config.TRADING['confidence_threshold']
        if signal['confidence'] < confidence_threshold:
            self.logger.info(f"Señal rechazada: confianza {signal['confidence']:.1%} < {confidence_threshold:.1%}")
            return False
        
        # Verificar límites de pérdida diaria
        if self.daily_pnl < -(self.config.TRADING['initial_capital'] * self.config.TRADING['max_daily_loss'] / 100):
            self.logger.warning("Límite de pérdida diaria alcanzado")
            return False
        
        return True
    
    def calculate_position_size(self, signal: Dict) -> float:
        """
        Calcular tamaño de posición basado en confianza
        
        Args:
            signal: Señal de trading
            
        Returns:
            Tamaño de posición en USD
        """
        base_size = self.config.TRADING['initial_capital'] * self.config.TRADING['position_size_percent']
        confidence_multiplier = signal['confidence']
        
        position_size = base_size * confidence_multiplier
        
        # Límites de seguridad
        min_size = 10  # Mínimo $10 para cumplir requisitos de Binance
        max_size = self.config.TRADING['initial_capital'] * 0.1  # Máximo 10%
        
        return max(min_size, min(position_size, max_size))
    
    def get_stop_loss_take_profit(self, signal: Dict) -> Tuple[float, float]:
        """
        Calcular stop loss y take profit
        
        Args:
            signal: Señal de trading
            
        Returns:
            Tupla (stop_loss, take_profit)
        """
        current_price = signal['current_price']
        stop_loss_pct = self.config.TRADING['stop_loss_percent'] / 100
        take_profit_pct = self.config.TRADING['take_profit_percent'] / 100
        
        if signal['signal'] == 'BUY':
            stop_loss = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + take_profit_pct)
        else:  # SELL
            stop_loss = current_price * (1 + stop_loss_pct)
            take_profit = current_price * (1 - take_profit_pct)
        
        return stop_loss, take_profit
    
    def get_trading_signal(self, historical_data: List[Dict]) -> Dict:
        """
        Obtener señal de trading según la estrategia
        
        Args:
            historical_data: Datos históricos
            
        Returns:
            Señal de trading completa
        """
        if self.strategy == 'breakout':
            return self.analyze_breakout_strategy(historical_data)
        elif self.strategy == 'scalping':
            return self.analyze_scalping_strategy(historical_data)
        else:
            return self._create_wait_signal(f"Estrategia {self.strategy} no implementada") 