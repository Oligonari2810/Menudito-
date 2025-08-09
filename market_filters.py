#!/usr/bin/env python3
"""
🔍 MARKET FILTERS - FILTROS DE ENTRADA FASE 1.6
Filtros de volatilidad, spread y volumen para mejorar rentabilidad
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from production_config import production_config

class MarketFilters:
    """Sistema de filtros de entrada para mejorar rentabilidad"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = production_config
        
        # Historial de filtros
        self.filter_history = []
        self.rejection_reasons = {
            'LOW_RANGE': 0,
            'HIGH_SPREAD': 0,
            'LOW_VOLUME': 0,
            'HIGH_WS_LAT': 0,
            'HIGH_REST_LAT': 0,
            'INVALID_PRICE': 0
        }
    
    def pre_trade_filters(self, market_data: Dict) -> Dict[str, Any]:
        """Aplicar todos los filtros previos al trade"""
        
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
            
            if range_bps < self.config.MIN_RANGE_BPS:
                filter_result['passed'] = False
                filter_result['reason'] = 'LOW_RANGE'
                filter_result['details']['min_range_bps'] = self.config.MIN_RANGE_BPS
                self.rejection_reasons['LOW_RANGE'] += 1
                self.logger.info(f"❌ Trade rechazado: Rango bajo {range_bps:.1f} bps < {self.config.MIN_RANGE_BPS} bps")
                return filter_result
        else:
            filter_result['passed'] = False
            filter_result['reason'] = 'INVALID_PRICE'
            self.rejection_reasons['INVALID_PRICE'] += 1
            return filter_result
        
        # 2. Filtro de spread
        if best_ask > 0 and best_bid > 0:
            mid_price = (best_ask + best_bid) / 2
            spread_pct = ((best_ask - best_bid) / mid_price) * 100
            spread_bps = spread_pct * 100  # convertir a bps
            
            filter_result['details']['spread_pct'] = spread_pct
            filter_result['details']['spread_bps'] = spread_bps
            
            if spread_bps > self.config.MAX_SPREAD_BPS:
                filter_result['passed'] = False
                filter_result['reason'] = 'HIGH_SPREAD'
                filter_result['details']['max_spread_bps'] = self.config.MAX_SPREAD_BPS
                self.rejection_reasons['HIGH_SPREAD'] += 1
                self.logger.info(f"❌ Trade rechazado: Spread alto {spread_bps:.1f} bps > {self.config.MAX_SPREAD_BPS} bps")
                return filter_result
        else:
            filter_result['warnings'].append("Spread no disponible")
        
        # 3. Filtro de volumen
        filter_result['details']['volume_usd'] = volume_usd
        
        if volume_usd < self.config.MIN_VOL_USD:
            filter_result['passed'] = False
            filter_result['reason'] = 'LOW_VOLUME'
            filter_result['details']['min_vol_usd'] = self.config.MIN_VOL_USD
            self.rejection_reasons['LOW_VOLUME'] += 1
            self.logger.info(f"❌ Trade rechazado: Volumen bajo ${volume_usd:,.0f} < ${self.config.MIN_VOL_USD:,.0f}")
            return filter_result
        
        # 4. Filtro de latencia WebSocket
        filter_result['details']['ws_latency_ms'] = ws_latency_ms
        
        if ws_latency_ms > self.config.MAX_WS_LATENCY_MS:
            filter_result['passed'] = False
            filter_result['reason'] = 'HIGH_WS_LAT'
            filter_result['details']['max_ws_latency_ms'] = self.config.MAX_WS_LATENCY_MS
            self.rejection_reasons['HIGH_WS_LAT'] += 1
            self.logger.info(f"❌ Trade rechazado: Latencia WS alta {ws_latency_ms:.1f}ms > {self.config.MAX_WS_LATENCY_MS}ms")
            return filter_result
        
        # 5. Filtro de latencia REST
        filter_result['details']['rest_latency_ms'] = rest_latency_ms
        
        if rest_latency_ms > self.config.MAX_REST_LATENCY_MS:
            filter_result['passed'] = False
            filter_result['reason'] = 'HIGH_REST_LAT'
            filter_result['details']['max_rest_latency_ms'] = self.config.MAX_REST_LATENCY_MS
            self.rejection_reasons['HIGH_REST_LAT'] += 1
            self.logger.info(f"❌ Trade rechazado: Latencia REST alta {rest_latency_ms:.1f}ms > {self.config.MAX_REST_LATENCY_MS}ms")
            return filter_result
        
        # Si pasa todos los filtros
        if filter_result['passed']:
            self.logger.info(f"✅ Filtros pasados: Rango={range_bps:.1f}bps, Spread={spread_bps:.1f}bps, Vol=${volume_usd:,.0f}")
        
        # Registrar en historial
        self.filter_history.append({
            'timestamp': datetime.now().isoformat(),
            'result': filter_result,
            'market_data': market_data
        })
        
        return filter_result
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Obtener resumen de filtros aplicados"""
        
        total_checks = len(self.filter_history)
        passed_checks = len([f for f in self.filter_history if f['result']['passed']])
        failed_checks = total_checks - passed_checks
        
        # Calcular porcentajes de rechazo por razón
        rejection_percentages = {}
        if total_checks > 0:
            for reason, count in self.rejection_reasons.items():
                rejection_percentages[reason] = (count / total_checks) * 100
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'pass_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            'rejection_reasons': self.rejection_reasons,
            'rejection_percentages': rejection_percentages,
            'last_check': self.filter_history[-1] if self.filter_history else None
        }
    
    def simulate_market_data(self, base_price: float = 600.0) -> Dict[str, Any]:
        """Simular datos de mercado para testing"""
        
        import random
        
        # Simular volatilidad
        volatility = random.uniform(0.001, 0.05)  # 0.1% a 5%
        high = base_price * (1 + volatility)
        low = base_price * (1 - volatility)
        close = base_price
        
        # Simular spread
        spread_bps = random.uniform(0.5, 3.0)  # 0.5 a 3 bps
        spread_pct = spread_bps / 10000
        best_ask = close * (1 + spread_pct / 2)
        best_bid = close * (1 - spread_pct / 2)
        
        # Simular volumen
        volume_usd = random.uniform(1000000, 10000000)  # 1M a 10M USD
        
        # Simular latencias
        ws_latency_ms = random.uniform(50, 200)
        rest_latency_ms = random.uniform(100, 500)
        
        return {
            'price': close,
            'high': high,
            'low': low,
            'close': close,
            'best_ask': best_ask,
            'best_bid': best_bid,
            'volume_usd': volume_usd,
            'ws_latency_ms': ws_latency_ms,
            'rest_latency_ms': rest_latency_ms
        }
    
    def test_filters(self, num_tests: int = 100) -> Dict[str, Any]:
        """Probar filtros con datos simulados"""
        
        test_results = {
            'total_tests': num_tests,
            'passed_tests': 0,
            'failed_tests': 0,
            'rejection_breakdown': {},
            'avg_range_bps': 0,
            'avg_spread_bps': 0,
            'avg_volume_usd': 0
        }
        
        ranges = []
        spreads = []
        volumes = []
        
        for i in range(num_tests):
            market_data = self.simulate_market_data()
            filter_result = self.pre_trade_filters(market_data)
            
            if filter_result['passed']:
                test_results['passed_tests'] += 1
            else:
                test_results['failed_tests'] += 1
                reason = filter_result['reason']
                test_results['rejection_breakdown'][reason] = test_results['rejection_breakdown'].get(reason, 0) + 1
            
            # Acumular métricas
            ranges.append(filter_result['details'].get('range_bps', 0))
            spreads.append(filter_result['details'].get('spread_bps', 0))
            volumes.append(filter_result['details'].get('volume_usd', 0))
        
        # Calcular promedios
        if ranges:
            test_results['avg_range_bps'] = sum(ranges) / len(ranges)
        if spreads:
            test_results['avg_spread_bps'] = sum(spreads) / len(spreads)
        if volumes:
            test_results['avg_volume_usd'] = sum(volumes) / len(volumes)
        
        return test_results

# Instancia global
market_filters = MarketFilters()
