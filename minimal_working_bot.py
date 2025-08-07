#!/usr/bin/env python3
"""
🤖 Bot Mínimo Funcional - Optimizado para Plan Gratuito
Versión simplificada que funciona sin dependencias problemáticas
"""

import os
import sys
import time
import json
import logging
import requests
import signal
from datetime import datetime
from typing import Dict, List

# Configurar logging optimizado para Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class GoogleSheetsLogger:
    """Logger simple para Google Sheets"""
    
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
    
    def log_trade(self, trade_data: Dict) -> bool:
        """Log trade a Google Sheets"""
        if not self.sheets_enabled:
            return False
            
        try:
            import gspread
            
            # Abrir o crear spreadsheet
            try:
                # Usar ID específico del spreadsheet existente
                spreadsheet = self.client.open_by_key("1aks2jTMCacJ5rdigtolhHB3JiSw5B8rWDHYT_rjk69U")
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(self.spreadsheet_name)
                self.logger.info(f"✅ Spreadsheet creado: {self.spreadsheet_name}")
            
            # Abrir o crear worksheet
            try:
                worksheet = spreadsheet.worksheet(self.worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=10)
                # Agregar headers
                headers = ['Timestamp', 'Symbol', 'Side', 'Price', 'Amount', 'Result', 'P&L', 'Capital']
                worksheet.append_row(headers)
                self.logger.info(f"✅ Worksheet creado: {self.worksheet_name}")
            
            # Preparar datos
            row_data = [
                trade_data.get('timestamp', ''),
                trade_data.get('symbol', ''),
                trade_data.get('side', ''),
                trade_data.get('price', ''),
                trade_data.get('amount', ''),
                trade_data.get('result', ''),
                trade_data.get('pnl', ''),
                trade_data.get('capital', '')
            ]
            
            # Agregar fila
            worksheet.append_row(row_data)
            self.logger.info("✅ Trade registrado en Google Sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando en Google Sheets: {e}")
            return False

class MinimalTradingBot:
    """Bot de trading mínimo funcional optimizado para plan gratuito"""
    
    def __init__(self):
        self.is_running = True
        self.counter = 0
        self.logger = logging.getLogger(__name__)
        
        # Configuración básica
        self.symbol = "BTCUSDT"
        self.initial_capital = 50.0
        self.current_capital = 50.0
        
        # Simular datos de trading
        self.trades_history = []
        self.daily_pnl = 0.0
        
        # Configurar Google Sheets
        self.sheets_logger = GoogleSheetsLogger()
        
        # Configurar manejo de señales
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        
    def handle_shutdown(self, signum, frame):
        """Manejar cierre graceful"""
        self.logger.info("🛑 Señal de terminación recibida")
        self.is_running = False
        
    def test_environment(self):
        """Probar variables de entorno"""
        required_vars = [
            'BINANCE_API_KEY',
            'BINANCE_SECRET_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(f"Variables faltantes: {missing_vars}")
            return False
        
        self.logger.info("✅ Variables de entorno configuradas")
        return True
    
    def send_telegram_message(self, message: str):
        """Enviar mensaje por Telegram con timeout optimizado"""
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
                # Timeout más corto para plan gratuito
                response = requests.post(url, json=data, timeout=5)
                if response.status_code == 200:
                    self.logger.info("✅ Mensaje enviado a Telegram")
                    return True
                else:
                    self.logger.error(f"❌ Error Telegram: {response.status_code}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Error enviando Telegram: {e}")
            return False
    
    def simulate_trading_signal(self) -> Dict:
        """Simular señal de trading optimizada"""
        import random
        
        # Reducir frecuencia de señales para estabilidad
        if random.random() < 0.7:  # 70% de probabilidad de WAIT
            return {
                'signal': 'WAIT',
                'reason': 'Sin señales claras',
                'confidence': 0.0
            }
        
        signals = ["BUY", "SELL"]
        signal = random.choice(signals)
        
        # Simular precio de BTC
        btc_price = 115000 + random.uniform(-5000, 5000)
        
        return {
            'signal': signal,
            'reason': f'Señal simulada - {signal} BTC',
            'confidence': random.uniform(0.1, 0.8),
            'price': btc_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_trade(self, signal: Dict) -> Dict:
        """Simular operación de trading optimizada"""
        if signal['signal'] == 'WAIT':
            return None
        
        # Simular resultado con menos volatilidad
        import random
        success = random.choice([True, False])
        
        if success:
            profit = random.uniform(0.2, 1.0)  # Ganancias más conservadoras
            self.current_capital += profit
            self.daily_pnl += profit
            result = "GANANCIA"
        else:
            loss = random.uniform(0.1, 0.8)  # Pérdidas más conservadoras
            self.current_capital -= loss
            self.daily_pnl -= loss
            result = "PÉRDIDA"
        
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'side': signal['signal'],
            'price': signal['price'],
            'amount': 10.0,
            'result': result,
            'pnl': profit if success else -loss,
            'capital': self.current_capital
        }
        
        self.trades_history.append(trade)
        
        # Log a Google Sheets
        self.sheets_logger.log_trade(trade)
        
        return trade
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading optimizado"""
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
                    self.logger.info(f"💰 Trade: {trade['side']} {self.symbol} @ ${trade['price']:,.2f} - {trade['result']}")
                    
                    # Enviar alerta a Telegram solo ocasionalmente
                    if self.counter % 3 == 0:  # Cada 3 operaciones
                        alert_msg = f"🤖 BOT MÍNIMO\n\n💰 Trade: {trade['side']} {self.symbol}\n💵 Precio: ${trade['price']:,.2f}\n📊 Resultado: {trade['result']}\n💸 P&L: ${trade['pnl']:.2f}\n🏦 Capital: ${self.current_capital:.2f}"
                        self.send_telegram_message(alert_msg)
            else:
                self.logger.info("⏳ Esperando señales...")
            
            # Enviar reporte cada 20 ciclos (menos frecuente)
            if self.counter % 20 == 0:
                report_msg = f"📊 REPORTE BOT MÍNIMO\n\n🔄 Ciclos: {self.counter}\n💰 Capital: ${self.current_capital:.2f}\n📈 P&L Diario: ${self.daily_pnl:.2f}\n📊 Operaciones: {len(self.trades_history)}"
                self.send_telegram_message(report_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo: {e}")
    
    def start(self):
        """Iniciar bot optimizado para plan gratuito"""
        self.logger.info("🚀 Iniciando bot mínimo funcional optimizado...")
        
        # Probar entorno
        if not self.test_environment():
            self.logger.warning("⚠️ Algunas variables faltan, continuando...")
        
        # Enviar mensaje de inicio
        start_msg = "🤖 BOT MÍNIMO INICIADO\n\n✅ Optimizado para plan gratuito\n📊 Simulación estable\n🔄 Ciclos cada 120 segundos\n📱 Alertas reducidas\n📊 Google Sheets habilitado"
        self.send_telegram_message(start_msg)
        
        self.logger.info("✅ Bot mínimo iniciado correctamente")
        
        # Bucle principal optimizado
        while self.is_running:
            try:
                self.run_trading_cycle()
                # Intervalo más largo para estabilidad
                time.sleep(120)  # 2 minutos
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Bot detenido por usuario")
                break
            except Exception as e:
                self.logger.error(f"❌ Error en bucle principal: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

def main():
    """Función principal"""
    print("🤖 BOT MÍNIMO FUNCIONAL - OPTIMIZADO")
    print("=" * 50)
    
    try:
        bot = MinimalTradingBot()
        bot.start()
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
