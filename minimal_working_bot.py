#!/usr/bin/env python3
"""
🤖 TRADING BOT PROFESIONAL
Bot de trading optimizado para funcionar de forma profesional
"""

import os
import time
import logging
import signal
import random
from datetime import datetime
from typing import Dict
import requests

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GoogleSheetsLogger:
    """Logger profesional para Google Sheets"""
    
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
        """Log trade a Google Sheets con formato profesional"""
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
                worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=13)
                self.logger.info(f"✅ Worksheet creado: {self.worksheet_name}")
            
            # Preparar datos en formato profesional
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
                'BOT PROFESIONAL - Señal automática',  # IA Validación
                trade_data.get('result', ''),  # Resultado
                f"${trade_data.get('pnl', 0):,.2f}",  # P&L
                f"${trade_data.get('capital', 0):,.2f}"  # Balance
            ]
            
            # Agregar fila
            worksheet.append_row(row_data)
            self.logger.info("✅ Trade registrado en Google Sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando en Google Sheets: {e}")
            return False

class ProfessionalTradingBot:
    """Bot de trading profesional optimizado"""
    
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
        
        # Configurar Google Sheets
        self.sheets_logger = GoogleSheetsLogger()
        if self.sheets_logger.sheets_enabled:
            self.logger.info("✅ Google Sheets habilitado")
        else:
            self.logger.warning("⚠️ Google Sheets NO habilitado")
        
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
        """Simular operación de trading"""
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
        
        # Log a Google Sheets
        sheets_result = self.sheets_logger.log_trade(trade)
        if sheets_result:
            self.logger.info("✅ Trade registrado en Google Sheets")
        else:
            self.logger.warning("⚠️ Error registrando en Google Sheets")
        
        return trade
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading profesional"""
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
                    
                    # Enviar alerta a Telegram
                    alert_msg = f"🤖 BOT PROFESIONAL\n\n💰 Trade: {trade['side']} {self.symbol}\n💵 Precio: ${trade['price']:,.2f}\n📊 Resultado: {trade['result']}\n💸 P&L: ${trade['pnl']:.2f}\n🏦 Capital: ${self.current_capital:.2f}"
                    self.send_telegram_message(alert_msg)
            else:
                self.logger.info("⏳ Esperando señales...")
            
            # Enviar reporte cada 10 ciclos
            if self.counter % 10 == 0:
                report_msg = f"📊 REPORTE PROFESIONAL\n\n🔄 Ciclos: {self.counter}\n💰 Capital: ${self.current_capital:.2f}\n📈 P&L Diario: ${self.daily_pnl:.2f}\n📊 Operaciones: {len(self.trades_history)}"
                self.send_telegram_message(report_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo: {e}")
    
    def start(self):
        """Iniciar bot profesional"""
        self.logger.info("🚀 Iniciando bot profesional...")
        
        # Mensaje de inicio
        start_msg = "🤖 BOT PROFESIONAL INICIADO\n\n✅ Sistema optimizado\n📊 Trading automatizado\n🔄 Ciclos cada 60 segundos\n📱 Alertas profesionales\n📊 Google Sheets habilitado"
        self.send_telegram_message(start_msg)
        
        self.logger.info("✅ Bot profesional iniciado correctamente")
        self.logger.info("🔄 Iniciando bucle principal...")
        
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
    """Función principal"""
    print("🤖 BOT PROFESIONAL - SISTEMA OPTIMIZADO")
    print("=" * 50)
    
    try:
        bot = ProfessionalTradingBot()
        print("✅ Bot creado exitosamente")
        print("🚀 Iniciando bot...")
        bot.start()
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
