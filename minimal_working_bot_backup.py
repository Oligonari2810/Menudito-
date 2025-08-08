#!/usr/bin/env python3
"""
🤖 TRADING BOT PROFESIONAL - FASE 1: MÉTRICAS
Bot de trading optimizado con sistema de métricas avanzado
"""

import os
import time
import logging
import signal
import random
from datetime import datetime
from typing import Dict, List
import requests

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MetricsTracker:
    """Sistema de monitoreo de métricas clave"""
    
    def __init__(self, max_operations: int = 50):
        self.logger = logging.getLogger(__name__)
        self.max_operations = max_operations
        self.operations_history: List[Dict] = []
        self.peak_capital = 50.0
        self.current_capital = 50.0
        
    def add_operation(self, operation: Dict):
        """Añadir operación al historial"""
        try:
            # Añadir operación
            self.operations_history.append(operation)
            
            # Mantener solo las últimas max_operations
            if len(self.operations_history) > self.max_operations:
                self.operations_history = self.operations_history[-self.max_operations:]
            
            # Actualizar capital
            self.current_capital = operation.get('capital', self.current_capital)
            
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
        """Calcular Profit Factor de las últimas operaciones"""
        try:
            if not self.operations_history:
                return 0.0
            
            total_gains = sum(op.get('pnl', 0) for op in self.operations_history if op.get('pnl', 0) > 0)
            total_losses = abs(sum(op.get('pnl', 0) for op in self.operations_history if op.get('pnl', 0) < 0))
            
            if total_losses == 0:
                profit_factor = total_gains if total_gains > 0 else 0.0
            else:
                profit_factor = total_gains / total_losses
            
            self.logger.info(f"📈 Profit Factor calculado: {profit_factor:.2f} (Gains: ${total_gains:.2f}, Losses: ${total_losses:.2f})")
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
        """Obtener resumen completo de métricas"""
        try:
            metrics = {
                'win_rate': self.calculate_win_rate(),
                'profit_factor': self.calculate_profit_factor(),
                'drawdown': self.calculate_drawdown(),
                'total_operations': len(self.operations_history),
                'current_capital': self.current_capital,
                'peak_capital': self.peak_capital,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"📊 Métricas calculadas: WR={metrics['win_rate']:.2f}%, PF={metrics['profit_factor']:.2f}, DD={metrics['drawdown']:.2f}%")
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
    """Bot de trading profesional optimizado con métricas"""
    
    def __init__(self):
        self.is_running = True
        self.counter = 0
        self.logger = logging.getLogger(__name__)
        
        # Configuración profesional
        self.symbol = "BTCUSDT"
        self.initial_capital = 50.0
        self.current_capital = 50.0
        
        # Historial de trades
        self.trades_history = []
        self.daily_pnl = 0.0
        
        # Sistema de métricas FASE 1
        self.metrics_tracker = MetricsTracker(max_operations=50)
        self.logger.info("✅ Sistema de métricas inicializado")
        
        # Configurar Google Sheets
        self.sheets_logger = GoogleSheetsLogger()
        if self.sheets_logger.sheets_enabled:
            self.logger.info("✅ Google Sheets habilitado")
        else:
            self.logger.warning("⚠️ Google Sheets NO habilitado")
        
        # Configurar logging local
        self.local_logger = LocalLogger()
        self.logger.info("✅ Logging local habilitado")
        
        # Configurar manejo de señales
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        
    def handle_shutdown(self, signum, frame):
        """Manejar cierre graceful"""
        self.logger.info("🛑 Señal de terminación recibida")
        self.is_running = False
        
    def send_telegram_message(self, message: str):
        """Enviar mensaje por Telegram"""
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
                response = requests.post(url, json=data, timeout=5)
                if response.status_code == 200:
                    self.logger.info("✅ Mensaje enviado a Telegram")
                else:
                    self.logger.warning(f"⚠️ Error enviando a Telegram: {response.status_code}")
            else:
                self.logger.warning("⚠️ Telegram no configurado")
        except Exception as e:
            self.logger.error(f"❌ Error Telegram: {e}")
    
    def simulate_trading_signal(self) -> Dict:
        """Simular señal de trading profesional"""
        signals = [
            {'signal': 'BUY', 'reason': 'Soporte técnico alcanzado', 'price': random.uniform(110000, 120000)},
            {'signal': 'SELL', 'reason': 'Resistencia técnica alcanzada', 'price': random.uniform(110000, 120000)},
            {'signal': 'WAIT', 'reason': 'Mercado lateral', 'price': 0}
        ]
        return random.choice(signals)
    
    def simulate_trade(self, signal: Dict) -> Dict:
        """Simular operación de trading con métricas"""
        if signal['signal'] == 'WAIT':
            return None
        
        # Simular resultado
        success = random.choice([True, False])
        
        if success:
            profit = random.uniform(0.1, 0.5)  # Ganancias conservadoras
            self.current_capital += profit
            self.daily_pnl += profit
            result = "GANANCIA"
        else:
            loss = random.uniform(0.1, 0.3)  # Pérdidas controladas
            self.current_capital -= loss
            self.daily_pnl -= loss
            result = "PÉRDIDA"
        
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'side': signal['signal'],
            'price': signal['price'],
            'amount': random.uniform(0.0001, 0.001),
            'result': result,
            'pnl': profit if success else -loss,
            'capital': self.current_capital
        }
        
        self.trades_history.append(trade)
        
        # Añadir operación al sistema de métricas FASE 1
        self.metrics_tracker.add_operation(trade)
        
        # Obtener métricas actualizadas
        metrics = self.metrics_tracker.get_metrics_summary()
        
        # Log a Google Sheets con métricas
        sheets_result = self.sheets_logger.log_trade(trade, metrics)
        if sheets_result:
            self.logger.info("✅ Trade registrado en Google Sheets con métricas")
        else:
            self.logger.warning("⚠️ Error registrando en Google Sheets")
        
        # Log local
        local_result = self.local_logger.log_operation(trade)
        if local_result:
            self.logger.info("✅ Trade registrado localmente")
        else:
            self.logger.warning("⚠️ Error registrando localmente")
        
        return trade
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading profesional con métricas"""
        try:
            self.counter += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.logger.info(f"🔄 Ciclo {self.counter} - {current_time}")
            
            # Generar señal
            signal = self.simulate_trading_signal()
            self.logger.info(f"📊 Señal: {signal['signal']} - {signal['reason']}")
            
            # Ejecutar operación si hay señal
            if signal['signal'] != 'WAIT':
                trade = self.simulate_trade(signal)
                if trade:
                    # Obtener métricas actualizadas
                    metrics = self.metrics_tracker.get_metrics_summary()
                    
                    self.logger.info(f"💰 Trade: {trade['side']} {self.symbol} @ ${trade['price']:,.2f} - {trade['result']}")
                    self.logger.info(f"📊 Métricas: WR={metrics['win_rate']:.2f}%, PF={metrics['profit_factor']:.2f}, DD={metrics['drawdown']:.2f}%")
                    
                    # Enviar alerta a Telegram con métricas
                    alert_msg = f"🤖 BOT PROFESIONAL - FASE 1\n\n💰 Trade: {trade['side']} {self.symbol}\n💵 Precio: ${trade['price']:,.2f}\n📊 Resultado: {trade['result']}\n💸 P&L: ${trade['pnl']:.2f}\n🏦 Capital: ${self.current_capital:.2f}\n\n📈 Métricas:\n📊 Win Rate: {metrics['win_rate']:.2f}%\n📈 Profit Factor: {metrics['profit_factor']:.2f}\n📉 Drawdown: {metrics['drawdown']:.2f}%"
                    self.send_telegram_message(alert_msg)
            else:
                self.logger.info("⏳ Esperando señales...")
            
            # Enviar reporte cada 10 ciclos con métricas
            if self.counter % 10 == 0:
                metrics = self.metrics_tracker.get_metrics_summary()
                report_msg = f"📊 REPORTE PROFESIONAL - FASE 1\n\n🔄 Ciclos: {self.counter}\n💰 Capital: ${self.current_capital:.2f}\n📈 P&L Diario: ${self.daily_pnl:.2f}\n📊 Operaciones: {len(self.trades_history)}\n\n📈 Métricas:\n📊 Win Rate: {metrics['win_rate']:.2f}%\n📈 Profit Factor: {metrics['profit_factor']:.2f}\n📉 Drawdown: {metrics['drawdown']:.2f}%"
                self.send_telegram_message(report_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo: {e}")
    
    def start(self):
        """Iniciar bot profesional con métricas"""
        self.logger.info("🚀 Iniciando bot profesional - FASE 1...")
        
        # Mensaje de inicio con métricas
        start_msg = "🤖 BOT PROFESIONAL - FASE 1 INICIADO\n\n✅ Sistema de métricas activo\n📊 Trading automatizado\n🔄 Ciclos cada 60 segundos\n📱 Alertas con métricas\n📊 Google Sheets con métricas\n💾 Logging local activo\n\n📈 Métricas iniciales:\n📊 Win Rate: 0.00%\n📈 Profit Factor: 0.00\n📉 Drawdown: 0.00%"
        self.send_telegram_message(start_msg)
        
        self.logger.info("✅ Bot profesional - FASE 1 iniciado correctamente")
        self.logger.info("🔄 Iniciando bucle principal con métricas...")
        
        # Bucle principal profesional
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                self.logger.info(f"🔄 Iniciando ciclo {cycle_count}...")
                self.run_trading_cycle()
                self.logger.info(f"✅ Ciclo {cycle_count} completado, esperando 60s...")
                time.sleep(60)  # 1 minuto
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Bot detenido por usuario")
                break
            except Exception as e:
                self.logger.error(f"❌ Error en ciclo {cycle_count}: {e}")
                import traceback
                self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
                time.sleep(30)  # Esperar 30 segundos antes de reintentar

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
