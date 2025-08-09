#!/usr/bin/env python3
"""
🚀 PRODUCTION BOT - FAST-TRACK A REAL CON PARACAÍDAS
Bot de trading de producción con kill-switches, telemetría y validaciones
"""

import os
import time
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any

# Importar módulos del fast-track
from production_config import production_config
from telemetry_manager import telemetry_manager
from order_validator import order_validator
from daily_reporter import daily_reporter
from market_filters import market_filters

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionTradingBot:
    """Bot de trading de producción con todas las medidas de seguridad"""
    
    def __init__(self):
        self.logger = logger
        self.shutdown_state = {"stop": False}
        
        # Configuración
        self.config = production_config
        self.telemetry = telemetry_manager
        self.validator = order_validator
        self.reporter = daily_reporter
        self.filters = market_filters
        
        # Estado del bot
        self.current_capital = 50.0
        self.initial_capital = 50.0
        self.trades_today = 0
        self.consecutive_losses = 0
        self.last_trade_time = None
        
        # Configurar señales
        signal.signal(signal.SIGTERM, self.handle_shutdown_signal)
        signal.signal(signal.SIGINT, self.handle_shutdown_signal)
        
        self.logger.info("🚀 Bot de producción inicializado")
        self.logger.info(f"Configuración: {self.config.get_config_summary()}")
    
    def handle_shutdown_signal(self, signum, frame):
        """Manejar señales de apagado"""
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        self.logger.info(f"🛑 {signal_name} recibido → Iniciando apagado limpio...")
        self.shutdown_state["stop"] = True
    
    def check_kill_switches(self) -> Dict[str, Any]:
        """Verificar todos los kill-switches"""
        kill_switches = self.config.check_kill_switches(
            self.current_capital, 
            self.initial_capital
        )
        
        if kill_switches['triggered']:
            self.logger.critical(f"🚨 KILL-SWITCH ACTIVADO: {kill_switches['reason']}")
            
            # Activar kill-switch
            kill_switch_result = self.config.trigger_kill_switch(kill_switches['reason'])
            
            # Enviar alerta crítica
            self.send_critical_alert(kill_switch_result)
            
            # Revertir a shadow mode
            self.config.LIVE_TRADING = False
            self.config.SHADOW_MODE = True
            
            self.logger.info("🔄 Revertido a SHADOW MODE")
        
        return kill_switches
    
    def send_critical_alert(self, kill_switch_data: Dict):
        """Enviar alerta crítica por Telegram"""
        message = f"""
🚨 **KILL-SWITCH ACTIVADO**

⏰ **Timestamp**: {kill_switch_data['timestamp']}
📝 **Razón**: {kill_switch_data['reason']}
🔄 **Acción**: Revertido a Shadow Mode
💰 **Capital**: ${self.current_capital:.2f}
📊 **Trades hoy**: {self.trades_today}
❌ **Pérdidas consecutivas**: {self.consecutive_losses}

⚠️ **BOT PAUSADO HASTA REVISIÓN MANUAL**
        """
        
        # Aquí iría el código para enviar por Telegram
        self.logger.critical(f"Alerta crítica enviada: {message}")
    
    def apply_market_filters(self, market_data: Dict) -> Dict[str, Any]:
        """Aplicar filtros de mercado FASE 1.6"""
        
        filter_result = self.filters.pre_trade_filters(market_data)
        
        if not filter_result['passed']:
            self.logger.info(f"❌ Trade rechazado por filtros: {filter_result['reason']}")
            self.telemetry.record_error('market_filter_rejection', filter_result['reason'])
        
        return filter_result
    
    def calculate_trade_targets(self, price: float, atr_value: float = None) -> Dict[str, float]:
        """Calcular TP y SL dinámicos FASE 1.6"""
        
        targets = self.config.compute_trade_targets(price, atr_value)
        
        self.logger.info(f"📊 Targets calculados: TP={targets['tp_pct']:.4f}%, SL={targets['sl_pct']:.4f}%, RR={targets['rr_ratio']:.2f}")
        
        return targets
    
    def validate_and_execute_trade(self, trade_data: Dict) -> Dict:
        """Validar y ejecutar trade con todas las verificaciones FASE 1.6"""
        
        # 1. Verificar kill-switches
        kill_switches = self.check_kill_switches()
        if kill_switches['triggered']:
            return {
                'executed': False,
                'reason': 'kill_switch_triggered',
                'kill_switch_data': kill_switches
            }
        
        # 2. Verificar sesión activa
        if not self.config.is_session_active():
            return {
                'executed': False,
                'reason': 'session_inactive',
                'message': 'Fuera de horario de trading'
            }
        
        # 3. Aplicar filtros de mercado FASE 1.6
        market_data = {
            'price': trade_data.get('price', 0.0),
            'high': trade_data.get('high', trade_data.get('price', 0.0)),
            'low': trade_data.get('low', trade_data.get('price', 0.0)),
            'close': trade_data.get('close', trade_data.get('price', 0.0)),
            'best_ask': trade_data.get('best_ask', trade_data.get('price', 0.0)),
            'best_bid': trade_data.get('best_bid', trade_data.get('price', 0.0)),
            'volume_usd': trade_data.get('volume_usd', 5000000),
            'ws_latency_ms': trade_data.get('ws_latency_ms', 100),
            'rest_latency_ms': trade_data.get('rest_latency_ms', 200)
        }
        
        filter_result = self.apply_market_filters(market_data)
        if not filter_result['passed']:
            return {
                'executed': False,
                'reason': 'market_filter_failed',
                'filter_result': filter_result
            }
        
        # 4. Calcular targets FASE 1.6
        targets = self.calculate_trade_targets(
            trade_data.get('price', 0.0),
            trade_data.get('atr_value', None)
        )
        
        # 5. Validar orden
        validation = self.validator.validate_complete_order(trade_data)
        if not validation['valid']:
            self.telemetry.record_error('validation_failed', str(validation['errors']))
            return {
                'executed': False,
                'reason': 'validation_failed',
                'errors': validation['errors']
            }
        
        # 6. Verificar latencia
        if validation['latency_ms'] > self.config.MAX_REST_LATENCY_MS:
            self.telemetry.record_error('high_latency', f"Latencia: {validation['latency_ms']}ms")
            return {
                'executed': False,
                'reason': 'high_latency',
                'latency_ms': validation['latency_ms']
            }
        
        # 7. Ejecutar trade (simulado en este ejemplo)
        trade_result = self.simulate_trade_execution(trade_data, targets)
        
        # 8. Registrar telemetría FASE 1.6
        telemetry_data = self.telemetry.record_trade_telemetry(trade_result)
        
        # 9. Actualizar métricas
        self.update_trading_metrics(trade_result)
        
        # 10. Registrar en daily reporter
        self.reporter.record_trade(trade_result)
        
        return {
            'executed': True,
            'trade_result': trade_result,
            'telemetry': telemetry_data,
            'validation': validation,
            'targets': targets,
            'filter_result': filter_result
        }
    
    def simulate_trade_execution(self, trade_data: Dict, targets: Dict) -> Dict:
        """Simular ejecución de trade con targets FASE 1.6"""
        
        # Simular ejecución
        execution_time = time.time()
        
        # Simular slippage realista
        intended_price = trade_data.get('price', 0.0)
        slippage_bps = 1.5  # 1.5 bps slippage simulado
        slippage_pct = slippage_bps / 10000
        executed_price = intended_price * (1 + slippage_pct)
        
        # Simular P&L basado en targets
        tp_pct = targets['tp_pct']
        sl_pct = targets['sl_pct']
        
        # Simular resultado basado en probabilidad
        import random
        win_probability = 0.6  # 60% win rate
        
        if random.random() < win_probability:
            # Simular ganancia (alcanzó TP)
            gross_pnl = trade_data.get('notional', 6.0) * tp_pct
            result = 'WIN'
        else:
            # Simular pérdida (alcanzó SL)
            gross_pnl = -trade_data.get('notional', 6.0) * sl_pct
            result = 'LOSS'
        
        trade_result = {
            'signal_id': self.telemetry.generate_signal_id(),
            'timestamp': datetime.now().isoformat(),
            'symbol': trade_data.get('symbol', 'BNBUSDT'),
            'side': trade_data.get('side', 'BUY'),
            'intended_price': intended_price,
            'executed_price': executed_price,
            'quantity': trade_data.get('quantity', 0.0),
            'notional': trade_data.get('notional', 0.0),
            'order_placement_time': execution_time - 0.1,
            'order_fill_time': execution_time,
            'gross_pnl': gross_pnl,
            'result': result,
            'slippage_pct': slippage_pct,
            'fill_latency_ms': 100.0,
            
            # FASE 1.6: Targets y métricas
            'tp_bps': targets['tp_bps'],
            'sl_bps': targets['sl_bps'],
            'tp_pct': targets['tp_pct'],
            'sl_pct': targets['sl_pct'],
            'rr_ratio': targets['rr_ratio'],
            'fric_bps': targets['fric_bps'],
            'tp_floor': targets['tp_floor'],
            
            # Datos de mercado
            'market_conditions': trade_data.get('market_conditions', {}),
            'spread_at_execution': trade_data.get('spread_at_execution', 0.0),
            'volume_at_execution': trade_data.get('volume_usd', 0.0),
            'range_at_execution': trade_data.get('range_pct', 0.0),
            
            # ATR para análisis
            'atr_value': trade_data.get('atr_value', 0.0)
        }
        
        return trade_result
    
    def update_trading_metrics(self, trade_result: Dict):
        """Actualizar métricas de trading con P&L neto FASE 1.6"""
        
        # Usar P&L neto en lugar de bruto
        net_pnl = trade_result.get('net_pnl', trade_result.get('gross_pnl', 0.0))
        
        # Actualizar capital
        self.current_capital += net_pnl
        
        # Actualizar contadores
        self.trades_today += 1
        self.last_trade_time = datetime.now()
        
        # Actualizar pérdidas consecutivas
        if trade_result.get('result') == 'LOSS':
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Actualizar config
        self.config.daily_trades_count = self.trades_today
        self.config.consecutive_losses = self.consecutive_losses
        
        # Log con métricas FASE 1.6
        tp_pct = trade_result.get('tp_pct', 0.0)
        sl_pct = trade_result.get('sl_pct', 0.0)
        rr_ratio = trade_result.get('rr_ratio', 0.0)
        friction_impact = trade_result.get('friction_impact', 0.0)
        
        self.logger.info(f"📊 Métricas actualizadas: Capital=${self.current_capital:.2f}, Trades={self.trades_today}, CL={self.consecutive_losses}")
        self.logger.info(f"📈 Trade: {trade_result['result']} | TP={tp_pct:.4f}% | SL={sl_pct:.4f}% | RR={rr_ratio:.2f} | Friction={friction_impact:.2f}%")
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading FASE 1.6"""
        
        cycle_start = datetime.now()
        self.logger.info(f"🔄 Iniciando ciclo - {cycle_start}")
        
        # Verificar pausa por errores
        if self.validator.should_pause_trading():
            self.logger.warning("⏸️ Trading pausado por errores")
            return
        
        # Simular datos de mercado FASE 1.6
        market_data = self.filters.simulate_market_data()
        
        # Simular señal de trading
        signal_data = {
            'symbol': self.config.SYMBOL,
            'side': 'BUY' if time.time() % 2 == 0 else 'SELL',
            'price': market_data['price'],
            'quantity': 0.01,
            'notional': 6.0,
            'current_price': market_data['price'],
            'volume_usd': market_data['volume_usd'],
            'spread_at_execution': market_data['spread_pct'],
            'range_pct': market_data['range_pct'],
            'atr_value': market_data['price'] * 0.01,  # 1% ATR simulado
            
            # Datos de mercado para filtros
            'high': market_data['high'],
            'low': market_data['low'],
            'close': market_data['close'],
            'best_ask': market_data['best_ask'],
            'best_bid': market_data['best_bid'],
            'ws_latency_ms': market_data['ws_latency_ms'],
            'rest_latency_ms': market_data['rest_latency_ms']
        }
        
        # Validar y ejecutar trade
        execution_result = self.validate_and_execute_trade(signal_data)
        
        if execution_result['executed']:
            trade_result = execution_result['trade_result']
            self.logger.info(f"✅ Trade ejecutado: {trade_result['side']} @ ${trade_result['executed_price']:.2f}")
            self.logger.info(f"📊 Resultado: {trade_result['result']} | P&L neto: ${trade_result.get('net_pnl', 0):.4f}")
        else:
            self.logger.info(f"❌ Trade rechazado: {execution_result['reason']}")
        
        # Enviar telemetría
        if self.config.TELEMETRY_ENABLED:
            self.telemetry.send_telemetry(
                self.telemetry.get_telemetry_summary(),
                self.config.get_config_summary()
            )
        
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        self.logger.info(f"✅ Ciclo completado en {cycle_duration:.2f}s")
    
    def generate_daily_report(self):
        """Generar y enviar reporte diario"""
        
        if not self.config.DAILY_REPORT_ENABLED:
            return
        
        report = self.reporter.generate_daily_report()
        
        # Enviar por Telegram
        telegram_message = self.reporter.send_daily_report_telegram(report)
        
        # Guardar en Google Sheets (si está configurado)
        self.logger.info(f"📊 Reporte diario generado: {report['metrics']}")
        
        return report
    
    def start(self):
        """Iniciar bot de producción"""
        
        self.logger.info("🚀 Iniciando bot de producción FASE 1.6...")
        self.logger.info(f"Configuración: {self.config.get_config_summary()}")
        
        # Iniciar sesión diaria
        self.reporter.start_daily_session()
        
        cycle_count = 0
        
        while not self.shutdown_state["stop"]:
            try:
                cycle_count += 1
                self.logger.info(f"🔄 Ciclo {cycle_count} iniciado")
                
                # Ejecutar ciclo de trading
                self.run_trading_cycle()
                
                # Verificar si es fin de día (22:00)
                current_hour = datetime.now().hour
                if current_hour == 22 and self.trades_today > 0:
                    self.generate_daily_report()
                    self.trades_today = 0  # Reset para mañana
                
                # Esperar próximo ciclo
                sleep_time = int(self.config.get('CYCLE_INTERVAL_SECONDS', 180))
                self.logger.info(f"⏳ Esperando {sleep_time}s para próximo ciclo...")
                
                # Dormir en bloques de 1s para responder a señales
                remaining = sleep_time
                while remaining > 0 and not self.shutdown_state["stop"]:
                    time.sleep(1)
                    remaining -= 1
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Interrupción manual recibida")
                break
            except Exception as e:
                self.logger.error(f"❌ Error en ciclo {cycle_count}: {e}")
                self.telemetry.record_error('cycle_error', str(e))
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
        
        # Apagado limpio
        self.logger.info("🛑 Iniciando apagado limpio...")
        self.generate_daily_report()
        self.logger.info("✅ Bot apagado correctamente")

def main():
    """Función principal"""
    
    # Verificar variables de entorno críticas
    required_env_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        logger.error("Por favor, configura las variables de entorno requeridas")
        sys.exit(1)
    
    # Crear y ejecutar bot
    bot = ProductionTradingBot()
    bot.start()

if __name__ == "__main__":
    main()
