#!/usr/bin/env python3
"""
🔍 ORDER VALIDATOR - VALIDACIONES PREVIAS A CADA ORDEN
Verificación de minNotional, stepSize, precision y latencia antes de ejecutar órdenes
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_DOWN
import requests

class OrderValidator:
    """Sistema de validaciones previas a cada orden"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuración de símbolos
        self.symbol_info = {
            'BNBUSDT': {
                'minNotional': 5.0,
                'stepSize': 0.001,
                'precision': 3,
                'baseAsset': 'BNB',
                'quoteAsset': 'USDT'
            }
        }
        
        # Historial de latencia
        self.latency_history = []
        self.failure_count = 0
        self.last_failure_time = None
        
        # Estado de pausa
        self.paused_until = None
        
    def validate_order_parameters(self, symbol: str, side: str, quantity: float, 
                                price: float, notional: float) -> Dict:
        """Validar parámetros de la orden antes de ejecutar"""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'adjusted_params': {}
        }
        
        # 1. Verificar símbolo
        if symbol not in self.symbol_info:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Símbolo no soportado: {symbol}")
            return validation_result
        
        symbol_config = self.symbol_info[symbol]
        
        # 2. Verificar minNotional
        if notional < symbol_config['minNotional']:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"Notional {notional} < minNotional {symbol_config['minNotional']}"
            )
        
        # 3. Verificar stepSize y precision
        quantity_decimal = Decimal(str(quantity))
        step_size_decimal = Decimal(str(symbol_config['stepSize']))
        
        # Redondear a stepSize
        adjusted_quantity = float(quantity_decimal.quantize(
            step_size_decimal, rounding=ROUND_DOWN
        ))
        
        if adjusted_quantity != quantity:
            validation_result['warnings'].append(
                f"Quantity ajustado: {quantity} → {adjusted_quantity}"
            )
            validation_result['adjusted_params']['quantity'] = adjusted_quantity
        
        # 4. Verificar precision del precio
        price_decimal = Decimal(str(price))
        precision_decimal = Decimal('0.001')  # 3 decimales para BNBUSDT
        
        adjusted_price = float(price_decimal.quantize(
            precision_decimal, rounding=ROUND_DOWN
        ))
        
        if adjusted_price != price:
            validation_result['warnings'].append(
                f"Price ajustado: {price} → {adjusted_price}"
            )
            validation_result['adjusted_params']['price'] = adjusted_price
        
        # 5. Verificar que la cantidad sea positiva
        if quantity <= 0:
            validation_result['valid'] = False
            validation_result['errors'].append("Quantity debe ser positiva")
        
        # 6. Verificar que el precio sea positivo
        if price <= 0:
            validation_result['valid'] = False
            validation_result['errors'].append("Price debe ser positivo")
        
        return validation_result
    
    def check_api_latency(self, endpoint: str = 'REST') -> Tuple[bool, float]:
        """Verificar latencia de API"""
        start_time = time.time()
        
        try:
            # Simular llamada a API (en producción sería real)
            if endpoint == 'REST':
                # Simular latencia de REST API
                time.sleep(0.1)  # 100ms simulado
            else:
                # Simular latencia de WebSocket
                time.sleep(0.05)  # 50ms simulado
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Registrar latencia
            latency_data = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'latency_ms': latency_ms,
                'status': 'OK' if latency_ms <= 1500 else 'SLOW'
            }
            self.latency_history.append(latency_data)
            
            # Verificar umbral
            is_acceptable = latency_ms <= 1500
            
            if not is_acceptable:
                self.logger.warning(f"Latencia alta: {latency_ms:.2f}ms en {endpoint}")
            
            return is_acceptable, latency_ms
            
        except Exception as e:
            self.logger.error(f"Error verificando latencia: {e}")
            return False, 9999.0
    
    def should_retry_order(self, attempt: int, max_attempts: int = 2) -> bool:
        """Verificar si debe reintentar la orden"""
        return attempt < max_attempts
    
    def should_pause_trading(self) -> bool:
        """Verificar si debe pausar trading por fallos"""
        if self.paused_until and datetime.now() < self.paused_until:
            return True
        
        # Si hay muchos fallos recientes, pausar
        if self.failure_count >= 3:
            self.paused_until = datetime.now().replace(
                minute=datetime.now().minute + 15
            )
            self.failure_count = 0
            return True
        
        return False
    
    def record_failure(self, failure_type: str, error_message: str):
        """Registrar fallo"""
        self.failure_count += 1
        self.last_failure_time = datetime.now().isoformat()
        
        failure_data = {
            'timestamp': self.last_failure_time,
            'failure_type': failure_type,
            'error_message': error_message,
            'failure_count': self.failure_count
        }
        
        self.logger.error(f"Fallo registrado: {failure_type} - {error_message}")
        return failure_data
    
    def validate_market_conditions(self, symbol: str, current_price: float, 
                                 volume: float, spread: float) -> Dict:
        """Validar condiciones de mercado"""
        
        validation = {
            'valid': True,
            'warnings': [],
            'market_conditions': {
                'price': current_price,
                'volume': volume,
                'spread': spread
            }
        }
        
        # Verificar spread
        if spread > 0.1:  # Spread > 0.1%
            validation['warnings'].append(f"Spread alto: {spread:.4f}%")
        
        # Verificar volumen
        if volume < 1000:  # Volumen bajo
            validation['warnings'].append(f"Volumen bajo: {volume}")
        
        # Verificar precio
        if current_price <= 0:
            validation['valid'] = False
            validation['warnings'].append("Precio inválido")
        
        return validation
    
    def get_validation_summary(self) -> Dict:
        """Obtener resumen de validaciones"""
        if not self.latency_history:
            return {}
        
        latencies = [h['latency_ms'] for h in self.latency_history]
        
        return {
            'total_validations': len(self.latency_history),
            'avg_latency_ms': round(sum(latencies) / len(latencies), 2),
            'max_latency_ms': round(max(latencies), 2),
            'min_latency_ms': round(min(latencies), 2),
            'slow_responses': len([h for h in self.latency_history if h['status'] == 'SLOW']),
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'paused_until': self.paused_until.isoformat() if self.paused_until else None
        }
    
    def validate_complete_order(self, order_data: Dict) -> Dict:
        """Validación completa de orden"""
        
        # 1. Validar parámetros básicos
        param_validation = self.validate_order_parameters(
            order_data.get('symbol', 'BNBUSDT'),
            order_data.get('side', 'BUY'),
            order_data.get('quantity', 0.0),
            order_data.get('price', 0.0),
            order_data.get('notional', 0.0)
        )
        
        # 2. Verificar latencia
        latency_ok, latency_ms = self.check_api_latency('REST')
        
        # 3. Verificar condiciones de mercado
        market_validation = self.validate_market_conditions(
            order_data.get('symbol', 'BNBUSDT'),
            order_data.get('current_price', 0.0),
            order_data.get('volume', 0.0),
            order_data.get('spread', 0.0)
        )
        
        # 4. Resultado final
        final_validation = {
            'valid': param_validation['valid'] and latency_ok and market_validation['valid'],
            'errors': param_validation['errors'] + ([] if latency_ok else ['Latencia alta']),
            'warnings': param_validation['warnings'] + market_validation['warnings'],
            'adjusted_params': param_validation['adjusted_params'],
            'latency_ms': latency_ms,
            'market_conditions': market_validation['market_conditions']
        }
        
        return final_validation

# Instancia global
order_validator = OrderValidator()
