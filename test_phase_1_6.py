#!/usr/bin/env python3
"""
🧪 TEST PHASE 1.6 - VALIDACIÓN DE MEJORAS DE RENTABILIDAD Y ROBUSTEZ
Script de pruebas para validar TP/SL dinámicos, filtros y P&L realista
"""

import logging
import time
from datetime import datetime
from typing import Dict, List

# Importar módulos
from production_config import production_config
from market_filters import market_filters
from telemetry_manager import telemetry_manager
from order_validator import order_validator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase16Tester:
    """Tester para validar mejoras de FASE 1.6"""
    
    def __init__(self):
        self.config = production_config
        self.filters = market_filters
        self.telemetry = telemetry_manager
        self.validator = order_validator
        
        self.test_results = {
            'tp_sl_tests': [],
            'filter_tests': [],
            'pnl_tests': [],
            'latency_tests': []
        }
    
    def test_tp_sl_calculation(self) -> Dict:
        """Probar cálculo de TP/SL dinámicos"""
        
        logger.info("🧪 Probando cálculo de TP/SL dinámicos...")
        
        test_cases = [
            {'price': 600.0, 'atr': None, 'mode': 'fixed_min'},
            {'price': 600.0, 'atr': 6.0, 'mode': 'atr_dynamic'},
            {'price': 1000.0, 'atr': 10.0, 'mode': 'atr_dynamic'},
            {'price': 500.0, 'atr': 5.0, 'mode': 'atr_dynamic'}
        ]
        
        results = []
        
        for case in test_cases:
            # Configurar modo
            self.config.TP_MODE = case['mode']
            
            # Calcular targets
            targets = self.config.compute_trade_targets(case['price'], case['atr'])
            
            # Validar resultados
            test_result = {
                'test_case': case,
                'targets': targets,
                'passed': True,
                'errors': []
            }
            
            # Verificar que TP nunca sea menor que el floor
            if targets['tp_bps'] < targets['tp_floor']:
                test_result['passed'] = False
                test_result['errors'].append(f"TP {targets['tp_bps']} < floor {targets['tp_floor']}")
            
            # Verificar RR ≥ 1.25
            if targets['rr_ratio'] < 1.25:
                test_result['passed'] = False
                test_result['errors'].append(f"RR {targets['rr_ratio']} < 1.25")
            
            # Verificar que SL sea positivo
            if targets['sl_bps'] <= 0:
                test_result['passed'] = False
                test_result['errors'].append(f"SL {targets['sl_bps']} <= 0")
            
            results.append(test_result)
            
            logger.info(f"✅ Test TP/SL: {case['mode']} | TP={targets['tp_pct']:.4f}% | SL={targets['sl_pct']:.4f}% | RR={targets['rr_ratio']:.2f}")
        
        self.test_results['tp_sl_tests'] = results
        return results
    
    def test_market_filters(self) -> Dict:
        """Probar filtros de mercado"""
        
        logger.info("🧪 Probando filtros de mercado...")
        
        # Probar con datos simulados
        test_results = self.filters.test_filters(num_tests=100)
        
        logger.info(f"✅ Filtros: {test_results['passed_tests']}/{test_results['total_tests']} pasaron")
        logger.info(f"📊 Rechazos: {test_results['rejection_breakdown']}")
        
        self.test_results['filter_tests'] = test_results
        return test_results
    
    def test_pnl_realistic(self) -> Dict:
        """Probar cálculo de P&L realista con fees/slippage"""
        
        logger.info("🧪 Probando P&L realista...")
        
        test_trades = [
            {
                'notional': 6.0,
                'intended_price': 600.0,
                'executed_price': 600.09,  # 1.5 bps slippage
                'gross_pnl': 0.05
            },
            {
                'notional': 10.0,
                'intended_price': 1000.0,
                'executed_price': 1000.015,  # 1.5 bps slippage
                'gross_pnl': -0.03
            },
            {
                'notional': 5.0,
                'intended_price': 500.0,
                'executed_price': 500.0075,  # 1.5 bps slippage
                'gross_pnl': 0.02
            }
        ]
        
        results = []
        
        for trade in test_trades:
            # Calcular P&L neto
            pnl_data = self.telemetry.calculate_net_pnl(trade)
            friction_data = self.telemetry.calculate_fees_and_slippage(trade)
            
            test_result = {
                'trade': trade,
                'pnl_data': pnl_data,
                'friction_data': friction_data,
                'passed': True,
                'errors': []
            }
            
            # Verificar que P&L neto < P&L bruto
            if pnl_data['net_pnl'] >= pnl_data['gross_pnl']:
                test_result['passed'] = False
                test_result['errors'].append("P&L neto >= P&L bruto")
            
            # Verificar que friction sea positiva
            if friction_data['total_friction'] <= 0:
                test_result['passed'] = False
                test_result['errors'].append("Friction <= 0")
            
            # Verificar fees en bps
            expected_fees_bps = (self.config.FEE_TAKER_BPS * 2)  # entrada + salida
            if abs(friction_data['fees_bps'] - expected_fees_bps) > 0.1:
                test_result['passed'] = False
                test_result['errors'].append(f"Fees bps {friction_data['fees_bps']} != expected {expected_fees_bps}")
            
            results.append(test_result)
            
            logger.info(f"✅ P&L Test: Bruto=${pnl_data['gross_pnl']:.4f} | Neto=${pnl_data['net_pnl']:.4f} | Friction=${friction_data['total_friction']:.4f}")
        
        self.test_results['pnl_tests'] = results
        return results
    
    def test_latency_validation(self) -> Dict:
        """Probar validación de latencia"""
        
        logger.info("🧪 Probando validación de latencia...")
        
        test_cases = [
            {'latency_ms': 100, 'expected': True},
            {'latency_ms': 800, 'expected': True},
            {'latency_ms': 1500, 'expected': True},
            {'latency_ms': 1600, 'expected': False},
            {'latency_ms': 2000, 'expected': False}
        ]
        
        results = []
        
        for case in test_cases:
            is_acceptable = self.telemetry.check_latency_threshold(case['latency_ms'])
            
            test_result = {
                'latency_ms': case['latency_ms'],
                'expected': case['expected'],
                'actual': is_acceptable,
                'passed': is_acceptable == case['expected']
            }
            
            results.append(test_result)
            
            status = "✅" if test_result['passed'] else "❌"
            logger.info(f"{status} Latencia {case['latency_ms']}ms: {is_acceptable} (expected: {case['expected']})")
        
        self.test_results['latency_tests'] = results
        return results
    
    def test_order_validation(self) -> Dict:
        """Probar validación de órdenes"""
        
        logger.info("🧪 Probando validación de órdenes...")
        
        test_orders = [
            {
                'symbol': 'BNBUSDT',
                'side': 'BUY',
                'quantity': 0.01,
                'price': 600.0,
                'notional': 6.0,
                'expected': True
            },
            {
                'symbol': 'BNBUSDT',
                'side': 'BUY',
                'quantity': 0.001,  # Muy pequeño
                'price': 600.0,
                'notional': 0.6,  # < minNotional
                'expected': False
            },
            {
                'symbol': 'INVALID',
                'side': 'BUY',
                'quantity': 0.01,
                'price': 600.0,
                'notional': 6.0,
                'expected': False
            }
        ]
        
        results = []
        
        for order in test_orders:
            validation = self.validator.validate_complete_order(order)
            
            test_result = {
                'order': order,
                'validation': validation,
                'expected': order['expected'],
                'actual': validation['valid'],
                'passed': validation['valid'] == order['expected']
            }
            
            results.append(test_result)
            
            status = "✅" if test_result['passed'] else "❌"
            logger.info(f"{status} Orden {order['symbol']}: {validation['valid']} (expected: {order['expected']})")
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Ejecutar todas las pruebas"""
        
        logger.info("🚀 Iniciando pruebas FASE 1.6...")
        
        start_time = time.time()
        
        # Ejecutar pruebas
        tp_sl_results = self.test_tp_sl_calculation()
        filter_results = self.test_market_filters()
        pnl_results = self.test_pnl_realistic()
        latency_results = self.test_latency_validation()
        order_results = self.test_order_validation()
        
        # Calcular estadísticas
        total_tests = 0
        passed_tests = 0
        
        # TP/SL tests
        tp_sl_passed = sum(1 for r in tp_sl_results if r['passed'])
        total_tests += len(tp_sl_results)
        passed_tests += tp_sl_passed
        
        # Filter tests
        filter_passed = filter_results['passed_tests']
        total_tests += filter_results['total_tests']
        passed_tests += filter_passed
        
        # P&L tests
        pnl_passed = sum(1 for r in pnl_results if r['passed'])
        total_tests += len(pnl_results)
        passed_tests += pnl_passed
        
        # Latency tests
        latency_passed = sum(1 for r in latency_results if r['passed'])
        total_tests += len(latency_results)
        passed_tests += latency_passed
        
        # Order tests
        order_passed = sum(1 for r in order_results if r['passed'])
        total_tests += len(order_results)
        passed_tests += order_passed
        
        # Resumen final
        test_summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'execution_time': time.time() - start_time,
            'test_results': self.test_results,
            'all_passed': passed_tests == total_tests
        }
        
        logger.info("📊 RESUMEN DE PRUEBAS FASE 1.6:")
        logger.info(f"✅ Tests pasados: {passed_tests}/{total_tests}")
        logger.info(f"📈 Tasa de éxito: {test_summary['pass_rate']:.1f}%")
        logger.info(f"⏱️ Tiempo de ejecución: {test_summary['execution_time']:.2f}s")
        
        if test_summary['all_passed']:
            logger.info("🎉 ¡TODAS LAS PRUEBAS PASARON! FASE 1.6 lista para producción")
        else:
            logger.warning("⚠️ Algunas pruebas fallaron. Revisar antes de producción")
        
        return test_summary

def main():
    """Función principal"""
    
    tester = Phase16Tester()
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()
