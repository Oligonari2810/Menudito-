#!/usr/bin/env python3
"""
📊 TELEMETRY MANAGER - SISTEMA DE TELEMETRÍA AVANZADO
Tracking de slippage, latencia, P&L y comparación real vs testnet
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
import json
from production_config import production_config

class TelemetryManager:
    """Sistema de telemetría avanzado para producción"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = production_config
        
        # Tracking de métricas
        self.slippage_data = []
        self.fill_latency_data = []
        self.realized_pnl_data = []
        self.equity_curve = []
        
        # Comparación real vs testnet
        self.real_vs_testnet_comparison = []
        self.signal_id_counter = 0
        
        # Latencia tracking
        self.rest_latency_history = []
        self.websocket_latency_history = []
        
        # Errores y fallos
        self.error_count = 0
        self.failure_count = 0
        self.last_error_time = None
        
        # FASE 1.6: P&L realista
        self.fees_data = []
        self.slippage_costs = []
        self.net_pnl_data = []
        
    def generate_signal_id(self) -> str:
        """Generar ID único para señal"""
        self.signal_id_counter += 1
        timestamp = int(time.time())
        return f"signal_{timestamp}_{self.signal_id_counter}"
    
    def calculate_fees_and_slippage(self, trade_data: Dict) -> Dict[str, float]:
        """Calcular fees y slippage realistas"""
        
        notional = trade_data.get('notional', 0.0)
        intended_price = trade_data.get('intended_price', 0.0)
        executed_price = trade_data.get('executed_price', 0.0)
        side = trade_data.get('side', 'BUY')
        
        # Calcular fees (entrada + salida)
        fee_rate = self.config.FEE_TAKER_BPS / 10000  # convertir bps a decimal
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
    
    def calculate_net_pnl(self, trade_data: Dict) -> Dict[str, float]:
        """Calcular P&L neto incluyendo fees y slippage"""
        
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
    
    def record_trade_telemetry(self, trade_data: Dict) -> Dict:
        """Registrar telemetría completa de trade con P&L realista"""
        signal_id = self.generate_signal_id()
        
        # Calcular P&L neto
        pnl_data = self.calculate_net_pnl(trade_data)
        friction_data = self.calculate_fees_and_slippage(trade_data)
        
        # Obtener targets del trade
        targets = self.config.compute_trade_targets(
            trade_data.get('entry_price', 0.0),
            trade_data.get('atr_value', None)
        )
        
        telemetry = {
            'signal_id': signal_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': trade_data.get('symbol', 'BNBUSDT'),
            'side': trade_data.get('side', 'BUY'),
            'entry_price': trade_data.get('entry_price', 0.0),
            'quantity': trade_data.get('quantity', 0.0),
            'notional': trade_data.get('notional', 0.0),
            
            # Slippage tracking
            'intended_price': trade_data.get('intended_price', 0.0),
            'executed_price': trade_data.get('executed_price', 0.0),
            'slippage_pct': self.calculate_slippage(
                trade_data.get('intended_price', 0.0),
                trade_data.get('executed_price', 0.0)
            ),
            
            # Latencia tracking
            'order_placement_time': trade_data.get('order_placement_time', 0.0),
            'order_fill_time': trade_data.get('order_fill_time', 0.0),
            'fill_latency_ms': self.calculate_fill_latency(
                trade_data.get('order_placement_time', 0.0),
                trade_data.get('order_fill_time', 0.0)
            ),
            
            # P&L tracking (FASE 1.6)
            'gross_pnl': pnl_data['gross_pnl'],
            'net_pnl': pnl_data['net_pnl'],
            'fees_cost': pnl_data['fees_cost'],
            'slippage_cost': pnl_data['slippage_cost'],
            'total_friction': pnl_data['total_friction'],
            'friction_impact': pnl_data['friction_impact'],
            
            # Targets y métricas (FASE 1.6)
            'tp_bps': targets['tp_bps'],
            'sl_bps': targets['sl_bps'],
            'tp_pct': targets['tp_pct'],
            'sl_pct': targets['sl_pct'],
            'rr_ratio': targets['rr_ratio'],
            'fric_bps': targets['fric_bps'],
            'tp_floor': targets['tp_floor'],
            
            # Fees y slippage en bps
            'fees_bps': friction_data['fees_bps'],
            'slippage_bps': friction_data['slippage_bps'],
            
            # Estado del mercado
            'market_conditions': trade_data.get('market_conditions', {}),
            'spread_at_execution': trade_data.get('spread_at_execution', 0.0),
            'volume_at_execution': trade_data.get('volume_at_execution', 0.0),
            'range_at_execution': trade_data.get('range_at_execution', 0.0)
        }
        
        # Guardar en historial
        self.slippage_data.append(telemetry['slippage_pct'])
        self.fill_latency_data.append(telemetry['fill_latency_ms'])
        self.realized_pnl_data.append(telemetry['net_pnl'])  # Usar P&L neto
        self.fees_data.append(telemetry['fees_bps'])
        self.slippage_costs.append(telemetry['slippage_bps'])
        self.net_pnl_data.append(telemetry['net_pnl'])
        
        return telemetry
    
    def calculate_slippage(self, intended_price: float, executed_price: float) -> float:
        """Calcular slippage en porcentaje"""
        if intended_price == 0:
            return 0.0
        
        slippage = ((executed_price - intended_price) / intended_price) * 100
        return round(slippage, 4)
    
    def calculate_fill_latency(self, placement_time: float, fill_time: float) -> float:
        """Calcular latencia de fill en milisegundos"""
        if placement_time == 0 or fill_time == 0:
            return 0.0
        
        latency_ms = (fill_time - placement_time) * 1000
        return round(latency_ms, 2)
    
    def record_real_vs_testnet_comparison(self, real_trade: Dict, testnet_trade: Dict) -> Dict:
        """Comparar trade real vs testnet"""
        comparison = {
            'signal_id': real_trade.get('signal_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            
            # Precios
            'real_entry_price': real_trade.get('entry_price', 0.0),
            'testnet_entry_price': testnet_trade.get('entry_price', 0.0),
            'price_delta': real_trade.get('entry_price', 0.0) - testnet_trade.get('entry_price', 0.0),
            
            # Slippage
            'real_slippage': real_trade.get('slippage_pct', 0.0),
            'testnet_slippage': testnet_trade.get('slippage_pct', 0.0),
            'slippage_delta': real_trade.get('slippage_pct', 0.0) - testnet_trade.get('slippage_pct', 0.0),
            
            # Latencia
            'real_fill_latency': real_trade.get('fill_latency_ms', 0.0),
            'testnet_fill_latency': testnet_trade.get('fill_latency_ms', 0.0),
            'latency_delta': real_trade.get('fill_latency_ms', 0.0) - testnet_trade.get('fill_latency_ms', 0.0),
            
            # P&L (FASE 1.6 - usar neto)
            'real_pnl': real_trade.get('net_pnl', 0.0),
            'testnet_pnl': testnet_trade.get('net_pnl', 0.0),
            'pnl_delta': real_trade.get('net_pnl', 0.0) - testnet_trade.get('net_pnl', 0.0),
            
            # Fees y friction (FASE 1.6)
            'real_fees_bps': real_trade.get('fees_bps', 0.0),
            'testnet_fees_bps': testnet_trade.get('fees_bps', 0.0),
            'fees_delta': real_trade.get('fees_bps', 0.0) - testnet_trade.get('fees_bps', 0.0),
            
            'real_slippage_bps': real_trade.get('slippage_bps', 0.0),
            'testnet_slippage_bps': testnet_trade.get('slippage_bps', 0.0),
            'slippage_delta_bps': real_trade.get('slippage_bps', 0.0) - testnet_trade.get('slippage_bps', 0.0)
        }
        
        self.real_vs_testnet_comparison.append(comparison)
        return comparison
    
    def record_latency_check(self, latency_ms: float, endpoint: str):
        """Registrar latencia de API"""
        latency_data = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'latency_ms': latency_ms,
            'status': 'OK' if latency_ms <= 1500 else 'SLOW'
        }
        
        if endpoint == 'REST':
            self.rest_latency_history.append(latency_data)
        else:
            self.websocket_latency_history.append(latency_data)
        
        return latency_data
    
    def check_latency_threshold(self, latency_ms: float) -> bool:
        """Verificar si la latencia está dentro del umbral"""
        return latency_ms <= 1500
    
    def get_telemetry_summary(self) -> Dict:
        """Obtener resumen de telemetría con métricas FASE 1.6"""
        if not self.slippage_data:
            return {}
        
        avg_slippage = sum(self.slippage_data) / len(self.slippage_data)
        avg_fill_latency = sum(self.fill_latency_data) / len(self.fill_latency_data)
        total_net_pnl = sum(self.net_pnl_data)
        total_gross_pnl = sum(self.realized_pnl_data)
        
        # FASE 1.6: Métricas de friction
        avg_fees_bps = sum(self.fees_data) / len(self.fees_data) if self.fees_data else 0
        avg_slippage_bps = sum(self.slippage_costs) / len(self.slippage_costs) if self.slippage_costs else 0
        total_friction_impact = total_gross_pnl - total_net_pnl
        
        return {
            'total_trades': len(self.slippage_data),
            'avg_slippage_pct': round(avg_slippage, 4),
            'avg_fill_latency_ms': round(avg_fill_latency, 2),
            'total_gross_pnl': round(total_gross_pnl, 4),
            'total_net_pnl': round(total_net_pnl, 4),
            'total_friction_impact': round(total_friction_impact, 4),
            'avg_fees_bps': round(avg_fees_bps, 2),
            'avg_slippage_bps': round(avg_slippage_bps, 2),
            'max_slippage': round(max(self.slippage_data), 4),
            'min_slippage': round(min(self.slippage_data), 4),
            'max_latency': round(max(self.fill_latency_data), 2),
            'min_latency': round(min(self.fill_latency_data), 2),
            'error_count': self.error_count,
            'failure_count': self.failure_count,
            'friction_impact_pct': round((total_friction_impact / abs(total_gross_pnl) * 100) if total_gross_pnl != 0 else 0, 2)
        }
    
    def get_real_vs_testnet_summary(self) -> Dict:
        """Obtener resumen de comparación real vs testnet"""
        if not self.real_vs_testnet_comparison:
            return {}
        
        slippage_deltas = [c['slippage_delta'] for c in self.real_vs_testnet_comparison]
        latency_deltas = [c['latency_delta'] for c in self.real_vs_testnet_comparison]
        pnl_deltas = [c['pnl_delta'] for c in self.real_vs_testnet_comparison]
        fees_deltas = [c['fees_delta'] for c in self.real_vs_testnet_comparison]
        
        return {
            'comparison_count': len(self.real_vs_testnet_comparison),
            'avg_slippage_delta': round(sum(slippage_deltas) / len(slippage_deltas), 4),
            'avg_latency_delta': round(sum(latency_deltas) / len(latency_deltas), 2),
            'avg_pnl_delta': round(sum(pnl_deltas) / len(pnl_deltas), 4),
            'avg_fees_delta': round(sum(fees_deltas) / len(fees_deltas), 2),
            'max_slippage_delta': round(max(slippage_deltas), 4),
            'max_latency_delta': round(max(latency_deltas), 2),
            'max_pnl_delta': round(max(pnl_deltas), 4),
            'max_fees_delta': round(max(fees_deltas), 2)
        }
    
    def record_error(self, error_type: str, error_message: str):
        """Registrar error"""
        self.error_count += 1
        self.last_error_time = datetime.now().isoformat()
        
        error_data = {
            'timestamp': self.last_error_time,
            'error_type': error_type,
            'error_message': error_message,
            'error_count': self.error_count
        }
        
        self.logger.error(f"Error registrado: {error_type} - {error_message}")
        return error_data
    
    def should_pause_trading(self) -> bool:
        """Verificar si debe pausar trading por errores"""
        return self.error_count >= 3 or self.failure_count >= 2
    
    def export_telemetry_data(self) -> Dict:
        """Exportar todos los datos de telemetría"""
        return {
            'summary': self.get_telemetry_summary(),
            'real_vs_testnet': self.get_real_vs_testnet_summary(),
            'slippage_data': self.slippage_data,
            'fill_latency_data': self.fill_latency_data,
            'realized_pnl_data': self.realized_pnl_data,
            'net_pnl_data': self.net_pnl_data,
            'fees_data': self.fees_data,
            'slippage_costs': self.slippage_costs,
            'real_vs_testnet_comparison': self.real_vs_testnet_comparison,
            'rest_latency_history': self.rest_latency_history,
            'websocket_latency_history': self.websocket_latency_history,
            'error_count': self.error_count,
            'failure_count': self.failure_count,
            'last_error_time': self.last_error_time
        }

# Instancia global
telemetry_manager = TelemetryManager()
