#!/usr/bin/env python3
"""
🛡️ BOT DE TRADING SOBREVIVIENTE - $50 → $1000 en 25 días
Sistema que minimiza el riesgo de "muerte" el primer día
"""

import os
import sys
import time
import argparse
import schedule
from datetime import datetime, timedelta
from typing import Dict, List

# Importar módulos
from config_survivor_final import FinalSurvivorTradingConfig as SurvivorTradingConfig
from modules.trading_logic import TradingLogic
from modules.telegram_alert import TelegramAlert
from modules.ai_validator import AIValidator
from modules.logger import TradingLogger
from sheets_logger import init_sheets_logger, get_sheets_logger, log_trade_to_sheet
from modules.binance_client import BinanceTradingClient

class SurvivorTradingBot:
    """Bot de trading con modo supervivencia"""
    
    def __init__(self, strategy: str = 'breakout'):
        """
        Inicializar bot de supervivencia
        
        Args:
            strategy: Estrategia de trading
        """
        self.strategy = strategy
        self.config = SurvivorTradingConfig()
        
        # Validar configuración
        errors = self.config.validate_config()
        if errors:
            print("❌ Errores de configuración:")
            for error in errors:
                print(f"  {error}")
            raise ValueError("Configuración inválida")
        
        # Inicializar componentes
        self.logger = TradingLogger()
        self.trading_logic = TradingLogic(strategy)
        self.telegram = TelegramAlert()
        self.ai_validator = AIValidator()
        
        # Inicializar Google Sheets Logger
        self.sheets_logger = None
        try:
            if init_sheets_logger("Trading Bot Survivor"):
                self.sheets_logger = get_sheets_logger()
                self.logger.logger.info("✅ Google Sheets Logger configurado")
                if self.sheets_logger:
                    url = self.sheets_logger.get_spreadsheet_url()
                    if url:
                        self.logger.logger.info(f"📊 Spreadsheet URL: {url}")
            else:
                self.logger.logger.warning("⚠️ Google Sheets Logger no disponible")
        except Exception as e:
            self.logger.logger.warning(f"⚠️ Error configurando Google Sheets Logger: {e}")
        
        # Cliente de Binance
        self.binance_client = BinanceTradingClient(
            testnet=self.config.BINANCE['testnet']
        )
        
        # Estado del bot
        self.is_running = False
        self.trade_history = []
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.current_capital = self.config.TARGET['initial_capital']
        self.trades_today = 0
        self.last_trade_time = None
        
        # Estado de supervivencia
        self.survival_mode = True
        self.day_blocked = False
        self.daily_capital_used = 0.0
        self.max_daily_capital = self.current_capital * self.config.TRADING['daily_capital_limit']
        self.current_day = 1
        self.consecutive_losses = 0
        self.aggression_level = 1  # 1=conservador, 2=agresivo, 3=ultra-agresivo
        
        # Configuración de modos
        self.trading_mode = "survival"  # survival, aggressive
        self.mode_transition_threshold = 60.0  # Cambiar a agresivo cuando capital ≥ $60
        
        # Objetivo específico
        self.target_capital = self.config.TARGET['target_capital']
        self.days_remaining = self.config.TARGET['days_remaining']
        self.required_daily_return = self.config.TARGET['required_daily_return']
        
        self.logger.logger.info(f"🛡️ Bot de supervivencia iniciado: {strategy}")
        self.logger.logger.info(f"🎯 Objetivo: ${self.current_capital} → ${self.target_capital} en {self.days_remaining} días")
        self.logger.logger.info(f"🛡️ Modo supervivencia: ACTIVADO")
        self.logger.logger.info(f"💰 Capital diario disponible: ${self.max_daily_capital:.2f}")
        
        # Enviar alerta de inicio
        startup_config = {
            'strategy': strategy,
            'symbol': self.config.BINANCE['symbol'],
            'capital': self.current_capital,
            'target': self.target_capital,
            'days_remaining': self.days_remaining,
            'survival_mode': True,
            'daily_capital_limit': self.config.TRADING['daily_capital_limit']
        }
        self.telegram.send_startup_alert(startup_config)
    
    def check_survival_conditions(self) -> bool:
        """Verificar condiciones de supervivencia"""
        try:
            # Verificar si el día está bloqueado
            if self.day_blocked:
                self.logger.logger.warning("🛑 Día bloqueado por pérdida anterior")
                return False
            
            # Verificar límite de capital diario
            if self.daily_capital_used >= self.max_daily_capital:
                self.logger.logger.warning(f"🛑 Límite de capital diario alcanzado: ${self.daily_capital_used:.2f}")
                return False
            
            # Verificar pérdida diaria
            if self.daily_pnl < -(self.max_daily_capital * self.config.TRADING['max_daily_loss'] / 100):
                self.logger.logger.warning("🛑 Límite de pérdida diaria alcanzado")
                self.block_day()
                return False
            
            # Verificar drawdown total
            if self.total_pnl < -(self.config.TARGET['initial_capital'] * self.config.RISK_MANAGEMENT['max_drawdown']):
                self.logger.logger.warning("🛑 Máximo drawdown alcanzado")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(str(e), "Verificando condiciones de supervivencia")
            return False
    
    def block_day(self):
        """Bloquear el día tras pérdida significativa"""
        self.day_blocked = True
        self.logger.logger.warning("🛑 DÍA BLOQUEADO - Esperando 24 horas")
        
        # Enviar alerta de bloqueo
        alert_message = f"🛑 DÍA BLOQUEADO\n💰 Pérdida diaria: ${self.daily_pnl:.2f}\n📊 Capital restante: ${self.current_capital:.2f}\n⏰ Reanudación: Mañana"
        self.telegram.send_message(alert_message)
    
    def adjust_aggression_level(self):
        """Ajustar nivel de agresividad según rendimiento"""
        try:
            if self.total_pnl > 0 and self.consecutive_losses == 0:
                # Ganando - aumentar agresividad
                if self.aggression_level < 3:
                    self.aggression_level += 1
                    self.logger.logger.info(f"📈 Aumentando agresividad a nivel {self.aggression_level}")
            elif self.consecutive_losses >= 2:
                # Perdiendo - reducir agresividad
                if self.aggression_level > 1:
                    self.aggression_level -= 1
                    self.logger.logger.info(f"📉 Reduciendo agresividad a nivel {self.aggression_level}")
            
            # Ajustar parámetros según nivel
            if self.aggression_level == 1:
                # Conservador
                self.config.TRADING['confidence_threshold'] = 0.25
                self.config.TRADING['position_size_percent'] = 0.12
                self.config.TRADING['max_leverage'] = 2
            elif self.aggression_level == 2:
                # Agresivo
                self.config.TRADING['confidence_threshold'] = 0.20
                self.config.TRADING['position_size_percent'] = 0.15
                self.config.TRADING['max_leverage'] = 2
            else:
                # Ultra-agresivo
                self.config.TRADING['confidence_threshold'] = 0.15
                self.config.TRADING['position_size_percent'] = 0.18
                self.config.TRADING['max_leverage'] = 3
            
        except Exception as e:
            self.logger.log_error(str(e), "Ajustando nivel de agresividad")
    
    def log_signal_to_sheets(self, signal: Dict, ai_result: Dict, executed: bool = False):
        """Registrar señal analizada en Google Sheets"""
        try:
            if not self.sheets_logger:
                return False
            
            # Crear registro de señal
            signal_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': self.config.BINANCE['symbol'],
                'direction': signal.get('signal', 'WAIT'),
                'price': signal.get('current_price', 0),
                'amount': 0,  # Se calcula solo si se ejecuta
                'strategy': self.strategy,
                'confidence': signal.get('confidence', 0),
                'ia_validation': ai_result.get('ai_response', 'N/A') if ai_result else 'N/A',
                'result': 'EXECUTED' if executed else 'PENDING',
                'pnl': 0,  # Se calcula solo si se ejecuta
                'balance': self.current_capital,
                'mode': self.trading_mode.upper(),
                'aggression_level': self.aggression_level,
                'reason': signal.get('reason', 'N/A')
            }
            
            # Registrar en Google Sheets
            success = self.sheets_logger.log_trade_dict(signal_data)
            if success:
                self.logger.logger.info(f"📊 Señal registrada en Google Sheets: {signal_data['direction']} @ ${signal_data['price']:,.2f}")
            else:
                self.logger.logger.warning("❌ Error registrando señal en Google Sheets")
            
            return success
            
        except Exception as e:
            self.logger.log_error(str(e), "Registrando señal en Google Sheets")
            return False
    
    def check_mode_transition(self):
        """Verificar y realizar transición automática de modo"""
        if self.trading_mode == "survival" and self.current_capital >= self.mode_transition_threshold:
            # Transición a modo agresivo
            self.trading_mode = "aggressive"
            self.logger.logger.info("🚨 TRANSICIÓN DE MODO ACTIVADA")
            self.logger.logger.info("🛡️ → 🚀 Modo AGRESIVO ahora activo")
            self.logger.logger.info(f"📈 Capital actual: ${self.current_capital:.2f} USD")
            
            # Actualizar configuración para modo agresivo
            self.config.TRADING['confidence_threshold'] = 0.08  # 8%
            self.config.TRADING['take_profit_percent'] = 5.0   # 5%
            self.config.TRADING['stop_loss_percent'] = 1.0     # 1%
            self.config.TRADING['daily_capital_limit'] = 0.60  # 60%
            self.config.TRADING['max_trades_per_day'] = 15     # 15 trades/día
            
            # Recalcular capital diario
            self.max_daily_capital = self.current_capital * self.config.TRADING['daily_capital_limit']
            
            # Enviar alerta a Telegram
            try:
                alert_message = (
                    f"🚨 CAMBIO DE MODO ACTIVADO\n\n"
                    f"🛡️ → 🚀 Modo AGRESIVO ahora activo\n"
                    f"📈 Capital actual: ${self.current_capital:.2f} USD\n"
                    f"⚡ Take Profit: {self.config.TRADING['take_profit_percent']:.1f}%\n"
                    f"🛑 Stop Loss: {self.config.TRADING['stop_loss_percent']:.1f}%\n"
                    f"📊 Operaciones/día: {self.config.TRADING['max_trades_per_day']}\n"
                    f"💰 Capital diario: ${self.max_daily_capital:.2f}"
                )
                self.telegram.send_alert(alert_message)
            except Exception as e:
                self.logger.logger.warning(f"⚠️ Error enviando alerta de cambio de modo: {e}")
            
            # Registrar en Google Sheets
            if self.sheets_logger:
                try:
                    mode_change_data = {
                        'timestamp': datetime.now().isoformat(),
                        'event': 'MODE_TRANSITION',
                        'from_mode': 'survival',
                        'to_mode': 'aggressive',
                        'capital': self.current_capital,
                        'threshold': self.mode_transition_threshold
                    }
                    self.sheets_logger.log_trade_dict(mode_change_data)
                except Exception as e:
                    self.logger.logger.warning(f"⚠️ Error registrando cambio de modo en Sheets: {e}")
            
            return True
        
        return False
    
    def get_market_data(self) -> Dict:
        """Obtener datos del mercado"""
        try:
            # Obtener precio actual
            current_price = self.binance_client.get_current_price(
                self.config.BINANCE['symbol']
            )
            
            # Obtener datos históricos
            klines = self.binance_client.get_historical_klines(
                symbol=self.config.BINANCE['symbol'],
                interval='5m',
                limit=100
            )
            
            if not klines:
                return None
            
            # Convertir datos de Binance (lista de listas) a formato de diccionarios
            # Formato Binance: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
            historical_data = []
            for k in klines:
                historical_data.append({
                    'timestamp': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                    'close_time': k[6],
                    'quote_volume': float(k[7]),
                    'trades': int(k[8]),
                    'taker_buy_base': float(k[9]),
                    'taker_buy_quote': float(k[10])
                })
            
            # Calcular métricas adicionales
            prices = [float(k[4]) for k in klines]  # índice 4 = close
            volumes = [float(k[5]) for k in klines]  # índice 5 = volume
            
            # Calcular volatilidad
            price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = sum(abs(change) for change in price_changes) / len(price_changes)
            
            # Calcular momentum
            momentum = (prices[-1] - prices[0]) / prices[0] if len(prices) > 1 else 0
            
            return {
                'current_price': current_price,
                'historical_data': historical_data,
                'volatility': volatility,
                'momentum': momentum,
                'volume_24h': sum(volumes[-24:]) if len(volumes) >= 24 else sum(volumes),
                'change_24h': momentum * 100
            }
            
        except Exception as e:
            self.logger.log_error(str(e), "Obteniendo datos del mercado")
            return None
    
    def analyze_signal(self, market_data: Dict) -> Dict:
        """Analizar señal con estrategia de supervivencia"""
        try:
            # Usar lógica de trading existente
            signal = self.trading_logic.get_trading_signal(market_data['historical_data'])
            
            # Ajustar confianza según supervivencia
            if self.survival_mode:
                # En modo supervivencia, ser más selectivo
                signal['confidence'] = signal['confidence'] * 1.1  # Aumentar 10%
            
            # Ajustar según volatilidad
            if market_data['volatility'] > 0.02:
                signal['confidence'] = min(0.95, signal['confidence'] * 1.1)
            
            # Ajustar según momentum
            if abs(market_data['momentum']) > 0.01:
                signal['confidence'] = min(0.95, signal['confidence'] * 1.05)
            
            # Agregar información adicional
            signal['current_price'] = market_data['current_price']
            signal['volatility'] = market_data['volatility']
            signal['momentum'] = market_data['momentum']
            signal['survival_mode'] = self.survival_mode
            signal['aggression_level'] = self.aggression_level
            
            return signal
            
        except Exception as e:
            self.logger.log_error(str(e), "Analizando señal")
            return None
    
    def validate_with_ai(self, signal: Dict, market_data: Dict) -> Dict:
        """Validar señal con IA en modo supervivencia"""
        try:
            # Validar campos requeridos
            required_fields = ['signal', 'confidence', 'current_price']
            for field in required_fields:
                if field not in signal:
                    self.logger.log_error(f"Campo requerido '{field}' no encontrado en signal", "Validación IA")
                    return {
                        'validated': False,
                        'confidence': 0.0,
                        'reason': f'Señal incompleta - falta {field}',
                        'ai_response': 'RECHAZADO - Datos incompletos'
                    }
            
            # Validar con OpenAI
            ai_result = self.ai_validator.validate_signal(signal, market_data)
            
            # En modo supervivencia, ser más permisivo con CAUTELA
            if ai_result.get('ai_response', '').upper().find('CAUTELA') != -1:
                if signal['confidence'] >= 0.25:  # Umbral más alto para supervivencia
                    ai_result['validated'] = True
                    self.logger.logger.info(f"✅ Aceptando CAUTELA con confianza {signal['confidence']:.1%}")
            
            # Loggear validación
            self.logger.log_ai_validation(signal, ai_result)
            
            # Enviar alerta de validación
            if self.config.OPENAI['enabled']:
                self.telegram.send_ai_validation_alert(signal, ai_result)
            
            return ai_result
            
        except Exception as e:
            self.logger.log_error(str(e), "Validación con IA")
            return {
                'validated': True,
                'confidence': signal['confidence'],
                'reason': f'Error de IA: {e}',
                'ai_response': 'CAUTELA - Error de IA'
            }
    
    def should_execute_trade(self, signal: Dict, ai_result: Dict) -> bool:
        """Determinar si debe ejecutar operación (lógica de supervivencia)"""
        try:
            # Verificar condiciones de supervivencia
            if not self.check_survival_conditions():
                return False
            
            # Verificar límites diarios
            if self.trades_today >= self.config.TRADING['max_trades_per_day']:
                self.logger.logger.warning(f"Límite diario alcanzado: {self.trades_today} operaciones")
                return False
            
            # Verificar confianza mínima
            adjusted_confidence = ai_result.get('confidence', signal['confidence'])
            if adjusted_confidence < self.config.TRADING['confidence_threshold']:
                self.logger.logger.info(f"Señal rechazada: confianza {adjusted_confidence:.1%} < {self.config.TRADING['confidence_threshold']:.1%}")
                return False
            
            # Verificar tiempo mínimo entre operaciones
            if self.last_trade_time:
                time_since_last = (datetime.now() - self.last_trade_time).total_seconds()
                if time_since_last < 30:  # Mínimo 30 segundos entre operaciones
                    return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(str(e), "Verificando ejecución de operación")
            return False
    
    def execute_trade(self, signal: Dict, ai_result: Dict) -> bool:
        """Ejecutar operación de trading con supervivencia"""
        try:
            # Verificar si debe ejecutar
            if not self.should_execute_trade(signal, ai_result):
                return False
            
            # Usar confianza ajustada por IA
            adjusted_confidence = ai_result.get('confidence', signal['confidence'])
            
            # Calcular tamaño de posición con límite diario
            base_size = min(
                self.current_capital * self.config.TRADING['position_size_percent'],
                self.max_daily_capital - self.daily_capital_used
            )
            confidence_multiplier = adjusted_confidence
            
            # Ajustar según rendimiento
            if self.total_pnl > 0:
                confidence_multiplier *= 1.1  # +10% si ganando
            
            position_size = base_size * confidence_multiplier
            
            # Límites de seguridad
            min_size = 10  # Mínimo $10
            max_size = self.max_daily_capital - self.daily_capital_used
            
            position_size = max(min_size, min(position_size, max_size))
            
            # Verificar balance
            balance = self.binance_client.get_account_balance('USDT')
            if balance < position_size:
                self.logger.logger.warning(f"Balance insuficiente: ${balance} < ${position_size}")
                return False
            
            # Calcular cantidad con precisión
            quantity = position_size / signal['current_price']
            quantity = round(quantity, 6)
            if quantity < 0.000001:
                quantity = 0.000001
            
            # Calcular stop loss y take profit
            stop_loss, take_profit = self.trading_logic.get_stop_loss_take_profit(signal)
            
            # Ejecutar orden
            if signal['signal'] == 'BUY':
                order = self.binance_client.place_market_buy_order(
                    symbol=self.config.BINANCE['symbol'],
                    quantity=quantity
                )
                side = 'BUY'
            else:  # SELL
                order = self.binance_client.place_market_sell_order(
                    symbol=self.config.BINANCE['symbol'],
                    quantity=quantity
                )
                side = 'SELL'
            
            # Crear registro de operación
            trade = {
                'id': order['orderId'],
                'side': side,
                'symbol': self.config.BINANCE['symbol'],
                'quantity': quantity,
                'price': signal['current_price'],
                'amount': position_size,
                'timestamp': datetime.now().isoformat(),
                'strategy': self.strategy,
                'confidence': adjusted_confidence,
                'signal': signal['signal'],
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'ai_validated': ai_result.get('validated', True),
                'ai_response': ai_result.get('ai_response', ''),
                'ai_validation': ai_result.get('ai_response', 'N/A'),
                'telegram_sent': True,
                'direction': side,
                'current_capital': self.current_capital,
                'target_progress': (self.current_capital / self.target_capital) * 100,
                'survival_mode': self.survival_mode,
                'aggression_level': self.aggression_level
            }
            
            # Loggear operación
            self.logger.log_trade(trade)
            
            # Enviar alerta de operación
            self.telegram.send_trade_alert(trade)
            
            # Registrar señal ejecutada en Google Sheets
            try:
                # Crear datos de señal ejecutada
                executed_signal_data = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': self.config.BINANCE['symbol'],
                    'direction': side,
                    'price': signal.get('current_price', 0),
                    'amount': position_size,
                    'strategy': self.strategy,
                    'confidence': signal.get('confidence', 0),
                    'ia_validation': ai_result.get('ai_response', 'N/A'),
                    'result': 'EXECUTED',
                    'pnl': simulated_pnl,
                    'balance': self.current_capital,
                    'mode': self.trading_mode.upper(),
                    'aggression_level': self.aggression_level,
                    'reason': signal.get('reason', 'N/A')
                }
                
                success = self.sheets_logger.log_trade_dict(executed_signal_data)
                if success:
                    self.logger.logger.info("✅ Operación registrada en Google Sheets")
                else:
                    self.logger.logger.warning("❌ Error registrando en Google Sheets")
            except Exception as e:
                self.logger.logger.error(f"Error guardando en Google Sheets: {e}")
            
            # Actualizar estado
            self.trade_history.append(trade)
            self.trades_today += 1
            self.last_trade_time = datetime.now()
            self.daily_capital_used += position_size
            
            # Simular P&L (en testnet)
            if side == 'BUY':
                simulated_pnl = position_size * 0.02
                self.current_capital += simulated_pnl
                self.total_pnl += simulated_pnl
                self.daily_pnl += simulated_pnl
                self.consecutive_losses = 0  # Resetear pérdidas consecutivas
            else:
                simulated_pnl = position_size * 0.015
                self.current_capital += simulated_pnl
                self.total_pnl += simulated_pnl
                self.daily_pnl += simulated_pnl
                self.consecutive_losses = 0  # Resetear pérdidas consecutivas
            
            # Ajustar agresividad
            self.adjust_aggression_level()
            
            self.logger.logger.info(f"💰 Capital actual: ${self.current_capital:.2f} (Objetivo: ${self.target_capital})")
            self.logger.logger.info(f"📈 Progreso: {(self.current_capital / self.target_capital) * 100:.1f}%")
            self.logger.logger.info(f"🛡️ Capital diario usado: ${self.daily_capital_used:.2f} / ${self.max_daily_capital:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.log_error(str(e), "Ejecutando operación")
            return False
    
    def run_trading_cycle(self):
        """Ejecutar un ciclo completo de trading con supervivencia"""
        try:
            self.logger.logger.info("🔄 Iniciando ciclo de trading con supervivencia...")
            
            # Verificar transición de modo automática
            mode_changed = self.check_mode_transition()
            if mode_changed:
                self.logger.logger.info("✅ Transición de modo completada")
            
            # Verificar si el día está bloqueado
            if self.day_blocked:
                self.logger.logger.info("⏳ Día bloqueado, esperando...")
                return
            
            # Obtener datos del mercado
            market_data = self.get_market_data()
            if not market_data:
                return
            
            # Analizar señal
            signal = self.analyze_signal(market_data)
            if not signal:
                return
            
            # Validar campos requeridos
            required_fields = ['signal', 'reason', 'current_price', 'confidence']
            for field in required_fields:
                if field not in signal:
                    self.logger.log_error(f"Campo requerido '{field}' no encontrado en signal", "Análisis de señal")
                    return
            
            # Mostrar información
            self.logger.logger.info(f"📊 Señal: {signal['signal']} - {signal['reason']}")
            self.logger.logger.info(f"💰 Precio: ${signal.get('current_price', 0):,.2f}")
            self.logger.logger.info(f"🎯 Confianza: {signal.get('confidence', 0):.1%}")
            self.logger.logger.info(f"🛡️ Modo supervivencia: {'ACTIVADO' if self.survival_mode else 'DESACTIVADO'}")
            self.logger.logger.info(f"📈 Nivel agresividad: {self.aggression_level}")
            self.logger.logger.info(f"🎯 Modo actual: {self.trading_mode.upper()}")
            
            # Validar con IA si hay señal
            if signal['signal'] != 'WAIT':
                ai_result = self.validate_with_ai(signal, market_data)
                
                # Registrar señal analizada en Google Sheets
                self.log_signal_to_sheets(signal, ai_result, executed=False)
                
                # Ejecutar operación si es válida
                if ai_result.get('validated', True):
                    success = self.execute_trade(signal, ai_result)
                    if success:
                        self.logger.logger.info("✅ Ciclo de supervivencia completado exitosamente")
                    else:
                        self.logger.logger.warning("⚠️ Ciclo completado con advertencias")
                else:
                    self.logger.logger.info("❌ Señal rechazada por IA")
            else:
                self.logger.logger.info("⏳ Sin señales de trading, esperando...")
            
        except Exception as e:
            self.logger.log_error(str(e), "Ciclo de trading con supervivencia")
    
    def reset_daily_limits(self):
        """Resetear límites diarios"""
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.daily_capital_used = 0.0
        self.day_blocked = False
        self.current_day += 1
        
        # Ajustar capital diario según progreso
        if self.current_capital > self.config.TARGET['initial_capital']:
            self.max_daily_capital = self.current_capital * self.config.TRADING['daily_capital_limit']
        
        self.logger.logger.info(f"📅 Día {self.current_day} - Límites reseteados")
        self.logger.logger.info(f"💰 Capital diario disponible: ${self.max_daily_capital:.2f}")
    
    def generate_daily_report(self):
        """Generar reporte diario de supervivencia"""
        try:
            # Calcular métricas
            daily_return = (self.daily_pnl / self.config.TARGET['initial_capital']) * 100
            total_return = (self.total_pnl / self.config.TARGET['initial_capital']) * 100
            target_progress = (self.current_capital / self.target_capital) * 100
            days_remaining = self.days_remaining - self.current_day
            
            # Crear reporte
            report = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'symbol': self.config.BINANCE['symbol'],
                'strategy': self.strategy,
                'trades_today': self.trades_today,
                'daily_pnl': self.daily_pnl,
                'total_pnl': self.total_pnl,
                'current_capital': self.current_capital,
                'target_capital': self.target_capital,
                'target_progress': target_progress,
                'daily_return': daily_return,
                'total_return': total_return,
                'days_remaining': days_remaining,
                'survival_mode': self.survival_mode,
                'aggression_level': self.aggression_level,
                'day_blocked': self.day_blocked
            }
            
            # Enviar reporte por Telegram
            self.telegram.send_daily_report(report)
            
            # Loggear resumen
            self.logger.logger.info(f"📊 REPORTE DIARIO DE SUPERVIVENCIA:")
            self.logger.logger.info(f"  • Operaciones: {self.trades_today}")
            self.logger.logger.info(f"  • P&L Diario: ${self.daily_pnl:.2f} ({daily_return:.1f}%)")
            self.logger.logger.info(f"  • P&L Total: ${self.total_pnl:.2f} ({total_return:.1f}%)")
            self.logger.logger.info(f"  • Capital Actual: ${self.current_capital:.2f}")
            self.logger.logger.info(f"  • Progreso Objetivo: {target_progress:.1f}%")
            self.logger.logger.info(f"  • Días Restantes: {days_remaining}")
            self.logger.logger.info(f"  • Modo Supervivencia: {'ACTIVADO' if self.survival_mode else 'DESACTIVADO'}")
            self.logger.logger.info(f"  • Nivel Agresividad: {self.aggression_level}")
            self.logger.logger.info(f"  • Día Bloqueado: {'SÍ' if self.day_blocked else 'NO'}")
            
            # Resetear límites diarios
            self.reset_daily_limits()
            
        except Exception as e:
            self.logger.log_error(str(e), "Generando reporte diario de supervivencia")
    
    def start(self):
        """Iniciar bot de supervivencia"""
        try:
            self.is_running = True
            self.logger.logger.info("🛡️ Iniciando bot de trading con supervivencia...")
            
            # Programar tareas
            schedule.every(self.config.TRADING['update_interval']).seconds.do(self.run_trading_cycle)
            schedule.every().day.at("00:00").do(self.generate_daily_report)
            
            # Bucle principal
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.logger.info("🛑 Bot detenido por usuario")
        except Exception as e:
            self.logger.log_error(str(e), "Ejecutando bot")
        finally:
            self.stop()
    
    def stop(self):
        """Detener bot"""
        self.is_running = False
        self.logger.logger.info("🛑 Bot de supervivencia detenido")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Bot de Trading con Supervivencia')
    parser.add_argument('--strategy', default='breakout', 
                       choices=['breakout', 'scalping', 'momentum'],
                       help='Estrategia de trading')
    
    args = parser.parse_args()
    
    # Mostrar configuración
    config = SurvivorTradingConfig()
    print(config.get_target_summary())
    
    try:
        # Crear y ejecutar bot
        bot = SurvivorTradingBot(args.strategy)
        bot.start()
        
    except Exception as e:
        print(f"❌ Error iniciando bot de supervivencia: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 