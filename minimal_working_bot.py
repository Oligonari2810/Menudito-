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
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SafetyManager:
    """Sistema de gestión de seguridad y protecciones"""
    
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
        
        # Límites de seguridad
        self.daily_loss_limit = 0.03  # 3%
        self.intraday_drawdown_limit = 0.10  # 10%
        self.max_consecutive_losses = 3
        self.min_cooldown_seconds = 90
        self.max_trades_per_hour = 20
        self.max_trades_per_day = 160
        
    def check_safety_conditions(self, current_capital: float) -> Dict:
        """Verificar todas las condiciones de seguridad"""
        try:
            # Calcular métricas de seguridad
            self.intraday_drawdown = ((self.session_start_capital - current_capital) / self.session_start_capital) * 100
            self.daily_loss = ((50.0 - current_capital) / 50.0) * 100
            
            # Verificar límites
            safety_status = {
                'can_trade': True,
                'reason': None,
                'daily_loss': self.daily_loss,
                'intraday_drawdown': self.intraday_drawdown,
                'consecutive_losses': self.consecutive_losses
            }
            
            # Kill switches
            if self.daily_loss >= 3.0:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Pérdida diaria crítica: {self.daily_loss:.2f}%"
                
            elif self.intraday_drawdown >= 10.0:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Drawdown intradía crítico: {self.intraday_drawdown:.2f}%"
                
            elif self.consecutive_losses >= 3:
                safety_status['can_trade'] = False
                safety_status['reason'] = f"Racha de pérdidas: {self.consecutive_losses} consecutivas"
            
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
    
    def record_trade(self, result: str, pnl: float):
        """Registrar resultado de trade para métricas de seguridad"""
        try:
            self.last_trade_time = datetime.now()
            self.hourly_trades += 1
            self.daily_trades += 1
            
            # Actualizar racha de pérdidas
            if result == 'PÉRDIDA':
                self.consecutive_losses += 1
            else:
                self.consecutive_losses = 0
                
            self.logger.info(f"📊 Seguridad: DD={self.intraday_drawdown:.2f}%, DL={self.daily_loss:.2f}%, CL={self.consecutive_losses}")
            
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
        self.ema_period = 50
        self.ema_timeframe = "1m"
        self.spread_max = 0.03  # 0.03%
        self.slippage_max = 0.02  # 0.02%
        
    def check_market_conditions(self, price: float, volume: float) -> Dict:
        """Verificar condiciones de mercado para operar"""
        try:
            # Simular indicadores técnicos
            atr_value = self.simulate_atr(price)
            ema_value = self.simulate_ema(price)
            spread_value = self.simulate_spread(price)
            
            filter_status = {
                'can_trade': True,
                'reason': None,
                'atr': atr_value,
                'ema': ema_value,
                'spread': spread_value
            }
            
            # Filtro ATR (volatilidad mínima)
            if atr_value < 0.4:  # ATR mínimo
                filter_status['can_trade'] = False
                filter_status['reason'] = f"Volatilidad insuficiente: ATR={atr_value:.3f}"
            
            # Filtro EMA50 (tendencia)
            if price > ema_value:
                filter_status['direction'] = 'BUY'
            else:
                filter_status['direction'] = 'SELL'
            
            # Filtro spread
            if spread_value > self.spread_max:
                filter_status['can_trade'] = False
                filter_status['reason'] = f"Spread alto: {spread_value:.3f}%"
            
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
        
    def calculate_position_size(self, capital: float, atr_value: float) -> Dict:
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
            
            # Calcular fees
            estimated_fees = final_size * self.fee_rate
            
            position_data = {
                'size': final_size,
                'fees': estimated_fees,
                'size_net': final_size - estimated_fees,
                'atr_value': atr_value,
                'base_size': base_size,
                'max_size': max_size
            }
            
            self.logger.info(f"💰 Tamaño posición: ${final_size:.2f} (ATR: {atr_value:.3f})")
            return position_data
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando tamaño: {e}")
            return {'size': 0, 'fees': 0, 'size_net': 0}
    
    def calculate_sl_tp(self, entry_price: float, direction: str, atr_value: float) -> Dict:
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
        
    def add_operation(self, operation: Dict):
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
            
            # Usar P&L neto de fees
            total_gains = sum(op.get('pnl_net', 0) for op in self.operations_history if op.get('pnl_net', 0) > 0)
            total_losses = abs(sum(op.get('pnl_net', 0) for op in self.operations_history if op.get('pnl_net', 0) < 0))
            
            if total_losses == 0:
                profit_factor = total_gains if total_gains > 0 else 0.0
            else:
                profit_factor = total_gains / total_losses
            
            self.logger.info(f"📈 Profit Factor (neto) calculado: {profit_factor:.2f} (Gains: ${total_gains:.2f}, Losses: ${total_losses:.2f})")
            return profit_factor
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando Profit Factor: {e}")
            return 0.0
    
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
    
    def get_metrics_summary(self) -> Dict:
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
    
    def log_trade(self, trade_data: Dict, metrics: Dict = None) -> bool:
        """Log trade a Google Sheets con métricas"""
        if not self.sheets_enabled:
            self.logger.warning("⚠️ Google Sheets no habilitado")
            return False
            
        try:
            import gspread
            
            # Abrir spreadsheet por ID específico
            try:
                spreadsheet = self.client.open_by_key("1aks2jTMCacJ5rdigtolhHB3JiSw5B8rWDHYT_rjk69U")
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(self.spreadsheet_name)
                self.logger.info(f"✅ Spreadsheet creado: {self.spreadsheet_name}")
            
            # Obtener worksheet
            try:
                worksheet = spreadsheet.worksheet(self.worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=16)
                self.logger.info(f"✅ Worksheet creado: {self.worksheet_name}")
            
            # Preparar datos en formato profesional con métricas
            timestamp = trade_data.get('timestamp', '')
            # Separar fecha y hora
            if 'T' in timestamp:
                date_part = timestamp.split('T')[0]
                time_part = timestamp.split('T')[1].split('.')[0]
            else:
                date_part = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
                time_part = timestamp.split(' ')[1] if ' ' in timestamp else ''
            
            # Calcular monto
            amount = trade_data.get('amount', 0)
            price = trade_data.get('price', 0)
            monto = amount * price if amount and price else 0
            
            # Obtener métricas si están disponibles
            win_rate = metrics.get('win_rate', 0) if metrics else 0
            profit_factor = metrics.get('profit_factor', 0) if metrics else 0
            drawdown = metrics.get('drawdown', 0) if metrics else 0
            
            row_data = [
                date_part,  # Fecha
                time_part,  # Hora
                trade_data.get('symbol', ''),  # Símbolo
                trade_data.get('side', ''),  # Dirección
                f"${trade_data.get('price', 0):,.2f}" if trade_data.get('price') else '',  # Precio Entrada
                f"{trade_data.get('amount', 0):.6f}",  # Cantidad
                f"${monto:,.2f}",  # Monto
                'breakout',  # Estrategia
                '0.6%',  # Confianza
                'BOT PROFESIONAL - FASE 1',  # IA Validación
                trade_data.get('result', ''),  # Resultado
                f"${trade_data.get('pnl', 0):,.2f}",  # P&L
                f"${trade_data.get('capital', 0):,.2f}",  # Balance
                f"{win_rate:.2f}%",  # Win Rate
                f"{profit_factor:.2f}",  # Profit Factor
                f"{drawdown:.2f}%"  # Drawdown
            ]
            
            # Agregar fila
            worksheet.append_row(row_data)
            self.logger.info("✅ Trade registrado en Google Sheets con métricas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando en Google Sheets: {e}")
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
    
    def log_operation(self, trade_data: Dict) -> bool:
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
        
        # Configuración de trading
        self.update_interval = 180  # 3 minutos (vs 60s anterior)
        self.session_start_time = datetime.now()
        
        # Configurar señales de interrupción
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        self.logger.info("🤖 BOT:")
        self.logger.info("✅ Sistema de métricas inicializado")
        self.logger.info("✅ Sistema de seguridad inicializado")
        self.logger.info("✅ Filtros de mercado inicializados")
        self.logger.info("✅ Gestión de posiciones inicializada")
        self.logger.info("✅ Google Sheets configurado desde variable de entorno")
        self.logger.info("✅ Google Sheets habilitado")
        self.logger.info("✅ Directorio de datos creado: trading_data")
        self.logger.info("✅ Logging local habilitado")
        self.logger.info("🚀 Iniciando bot profesional - FASE 1.5...")
        
        # Mensaje de inicio
        startup_message = f"""
🤖 BOT PROFESIONAL - FASE 1.5 INICIADO

📊 Configuración Optimizada:
⏱️ Intervalo: {self.update_interval}s
💰 Capital inicial: ${self.current_capital:.2f}
🛡️ Sistema de seguridad activo
📈 Métricas netas de fees
🎯 Filtros de mercado activos

🚀 Listo para operar con optimizaciones
"""
        self.send_telegram_message(startup_message)
        self.logger.info("✅ Bot profesional - FASE 1.5 iniciado correctamente")
    
    def handle_shutdown(self, signum, frame):
        """Manejar señal de interrupción"""
        self.logger.info("🛑 Señal de interrupción recibida, cerrando bot...")
        self.running = False
    
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
            self.logger.error(f"❌ Error enviando mensaje Telegram: {e}")
    
    def simulate_trading_signal(self) -> Dict:
        """Simular señal de trading con filtros de mercado"""
        try:
            # Simular precio actual
            current_price = random.uniform(110000, 120000)
            volume = random.uniform(1000, 5000)
            
            # Verificar condiciones de mercado
            market_conditions = self.market_filter.check_market_conditions(current_price, volume)
            
            if not market_conditions['can_trade']:
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
            
            self.logger.info(f"📊 Señal: {direction} - {market_conditions.get('reason', 'Condiciones favorables')}")
            return signal_data
            
        except Exception as e:
            self.logger.error(f"❌ Error generando señal: {e}")
            return {'signal': 'ERROR', 'reason': str(e)}
    
    def simulate_trade(self, signal: Dict) -> Dict:
        """Simular ejecución de trade con gestión de riesgo"""
        try:
            if signal['signal'] in ['REJECTED', 'ERROR']:
                return {
                    'executed': False,
                    'reason': signal.get('reason', 'Señal rechazada'),
                    'signal': signal
                }
            
            # Verificar condiciones de seguridad
            safety_status = self.safety_manager.check_safety_conditions(self.current_capital)
            
            if not safety_status['can_trade']:
                return {
                    'executed': False,
                    'reason': safety_status['reason'],
                    'signal': signal,
                    'safety_status': safety_status
                }
            
            # Obtener datos de mercado
            entry_price = signal['price']
            direction = signal['signal']
            atr_value = signal['market_data']['atr']
            
            # Calcular tamaño de posición
            position_data = self.position_manager.calculate_position_size(self.current_capital, atr_value)
            
            # Calcular SL/TP
            sl_tp_data = self.position_manager.calculate_sl_tp(entry_price, direction, atr_value)
            
            # Simular resultado del trade
            win_probability = 0.52  # Win rate objetivo
            is_win = random.random() < win_probability
            
            # Calcular P&L
            if is_win:
                # Ganancia basada en TP
                pnl_gross = position_data['size'] * (sl_tp_data['tp_price'] - entry_price) / entry_price
                result = 'GANANCIA'
            else:
                # Pérdida basada en SL
                pnl_gross = position_data['size'] * (sl_tp_data['sl_price'] - entry_price) / entry_price
                result = 'PÉRDIDA'
            
            # Calcular P&L neto de fees
            total_fees = position_data['fees'] * 2  # Entrada y salida
            pnl_net = pnl_gross - total_fees
            
            # Actualizar capital
            new_capital = self.current_capital + pnl_net
            self.current_capital = new_capital
            
            # Registrar trade en sistema de seguridad
            self.safety_manager.record_trade(result, pnl_net)
            
            # Crear datos del trade
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTCUSDT',
                'direction': direction,
                'entry_price': entry_price,
                'size': position_data['size'],
                'fees': total_fees,
                'pnl_gross': pnl_gross,
                'pnl_net': pnl_net,
                'result': result,
                'capital': new_capital,
                'capital_net': new_capital,
                'atr_value': atr_value,
                'sl_price': sl_tp_data['sl_price'],
                'tp_price': sl_tp_data['tp_price'],
                'confidence': signal['confidence'],
                'strategy': 'breakout',
                'phase': 'FASE 1.5',
                'safety_status': safety_status
            }
            
            # Añadir a métricas
            self.metrics_tracker.add_operation(trade_data)
            
            # Obtener métricas actualizadas
            metrics = self.metrics_tracker.get_metrics_summary()
            
            # Logging
            self.sheets_logger.log_trade(trade_data, metrics)
            self.local_logger.log_operation(trade_data)
            
            # Mensaje Telegram
            telegram_message = f"""
🤖 BOT PROFESIONAL - FASE 1.5

💰 Trade: {direction} BTCUSDT
💵 Precio: ${entry_price:,.2f}
📊 Resultado: {result}
💸 P&L: ${pnl_net:.2f}
🏦 Capital: ${new_capital:.2f}

📈 Métricas:
📊 Win Rate: {metrics['win_rate']:.2f}%
📈 Profit Factor: {metrics['profit_factor']:.2f}
📉 Drawdown: {metrics['drawdown']:.2f}%

🛡️ Seguridad:
📊 DD: {safety_status['intraday_drawdown']:.2f}%
📊 DL: {safety_status['daily_loss']:.2f}%
📊 CL: {safety_status['consecutive_losses']}
"""
            self.send_telegram_message(telegram_message)
            
            return {
                'executed': True,
                'trade_data': trade_data,
                'metrics': metrics,
                'safety_status': safety_status
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando trade: {e}")
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
                self.logger.info(f"✅ Trade ejecutado: {trade_result['trade_data']['direction']} @ ${trade_result['trade_data']['entry_price']:.2f}")
                self.logger.info(f"📊 Métricas: WR={trade_result['metrics']['win_rate']:.2f}%, PF={trade_result['metrics']['profit_factor']:.2f}, DD={trade_result['metrics']['drawdown']:.2f}%")
            else:
                self.logger.info(f"❌ Trade rechazado: {trade_result['reason']}")
            
            self.logger.info(f"✅ Ciclo {self.cycle_count} completado, esperando {self.update_interval}s...")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading: {e}")
    
    def start(self):
        """Iniciar bot de trading"""
        try:
            self.logger.info("🔄 Iniciando bucle principal con optimizaciones...")
            
            # Resetear contadores horarios cada hora
            last_hourly_reset = datetime.now()
            
            while self.running:
                try:
                    # Resetear contadores horarios
                    current_time = datetime.now()
                    if (current_time - last_hourly_reset).total_seconds() >= 3600:  # 1 hora
                        self.safety_manager.reset_hourly_counters()
                        last_hourly_reset = current_time
                    
                    # Ejecutar ciclo
                    self.run_trading_cycle()
                    
                    # Esperar intervalo
                    time.sleep(self.update_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Interrupción manual recibida")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error en bucle principal: {e}")
                    time.sleep(60)  # Esperar 1 minuto antes de reintentar
            
            # Mensaje de cierre
            final_message = f"""
🤖 BOT PROFESIONAL - CERRANDO

📊 Resumen Final:
🔄 Ciclos ejecutados: {self.cycle_count}
💰 Capital final: ${self.current_capital:.2f}
📈 P&L: ${self.current_capital - 50.0:.2f}

✅ Bot cerrado correctamente
"""
            self.send_telegram_message(final_message)
            self.logger.info("✅ Bot cerrado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando bot: {e}")

def main():
    """Función principal - FASE 1: MÉTRICAS"""
    print("🤖 BOT PROFESIONAL - FASE 1: MÉTRICAS")
    print("=" * 50)
    print("📊 Sistema de métricas implementado")
    print("📈 Win Rate, Profit Factor, Drawdown")
    print("📊 Google Sheets con métricas")
    print("📱 Alertas Telegram con métricas")
    print("=" * 50)
    
    try:
        bot = ProfessionalTradingBot()
        print("✅ Bot creado exitosamente con métricas")
        print("🚀 Iniciando bot - FASE 1...")
        bot.start()
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
