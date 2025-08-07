#!/usr/bin/env python3
"""
📊 Script para importar operaciones de Telegram a Google Sheets
Recupera datos de alertas de Telegram y los registra en Google Sheets
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict

class TelegramTradeImporter:
    """Importador de operaciones desde Telegram"""
    
    def __init__(self):
        self.sheets_logger = None
        self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Configurar Google Sheets"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                self.client = gspread.authorize(creds)
                self.sheets_logger = True
                print("✅ Google Sheets configurado correctamente")
            else:
                print("❌ credentials.json no encontrado")
                
        except Exception as e:
            print(f"❌ Error configurando Google Sheets: {e}")
    
    def parse_telegram_message(self, message: str) -> Dict:
        """Parsear mensaje de Telegram para extraer datos de trade"""
        try:
            # Patrón para mensajes de trade
            pattern = r"🤖 BOT MÍNIMO\n\n💰 Trade: (\w+) (\w+)\n💵 Precio: \$([\d,]+\.?\d*)\n📊 Resultado: (\w+)\n💸 P&L: \$(-?\d+\.?\d*)\n🏦 Capital: \$(\d+\.?\d*)"
            
            match = re.search(pattern, message)
            if match:
                side = match.group(1)
                symbol = match.group(2)
                price_str = match.group(3).replace(',', '')
                price = float(price_str)
                result = match.group(4)
                pnl_str = match.group(5)
                pnl = float(pnl_str)
                capital = float(match.group(6))
                
                # Generar timestamp en formato simple (como el original)
                yesterday = datetime.now() - timedelta(days=1)
                timestamp = yesterday.strftime("%Y-%m-%d\t%H:%M:%S")
                
                # Formatear precio con símbolo $ y comas
                price_formatted = f"${price:,.2f}"
                
                # Formatear P&L con símbolo $
                pnl_formatted = f"${pnl:.2f}"
                
                return {
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'side': side,
                    'price': price_formatted,
                    'amount': 10.0,
                    'result': result,
                    'pnl': pnl_formatted,
                    'capital': capital,
                    'strategy': 'breakout',
                    'confidence': '0.6%',
                    'ai_validation': 'CAUTELA - Señal con confianza moderada',
                    'status': 'EJECUTADO'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error parseando mensaje: {e}")
            return None
    
    def add_trade_to_sheets(self, trade_data: Dict) -> bool:
        """Agregar trade a Google Sheets"""
        if not self.sheets_logger:
            return False
            
        try:
            import gspread
            
            # Abrir spreadsheet
            spreadsheet_name = "Trading Bot Log"
            worksheet_name = "Trading Log"
            
            try:
                spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.client.create(spreadsheet_name)
                print(f"✅ Spreadsheet creado: {spreadsheet_name}")
            
            # Abrir worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=15)
                # Headers actualizados para coincidir con el formato original
                headers = ['Timestamp', 'Symbol', 'Side', 'Price', 'Amount', 'Strategy', 'Confidence', 'AI Validation', 'Status', 'P&L', 'Capital']
                worksheet.append_row(headers)
                print(f"✅ Worksheet creado: {worksheet_name}")
            
            # Preparar datos con formato correcto
            row_data = [
                trade_data.get('timestamp', ''),
                trade_data.get('symbol', ''),
                trade_data.get('side', ''),
                trade_data.get('price', ''),
                trade_data.get('amount', ''),
                trade_data.get('strategy', ''),
                trade_data.get('confidence', ''),
                trade_data.get('ai_validation', ''),
                trade_data.get('status', ''),
                trade_data.get('pnl', ''),
                trade_data.get('capital', '')
            ]
            
            # Agregar fila
            worksheet.append_row(row_data)
            print(f"✅ Trade importado: {trade_data['side']} {trade_data['symbol']} @ {trade_data['price']}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando a Google Sheets: {e}")
            return False
    
    def import_from_manual_data(self):
        """Importar datos manuales proporcionados por el usuario"""
        print("📊 IMPORTADOR DE OPERACIONES DE TELEGRAM")
        print("=" * 50)
        print("Pega los mensajes de Telegram uno por uno (escribe 'FIN' para terminar):")
        print()
        
        trades_imported = 0
        
        while True:
            message = input("📱 Mensaje de Telegram (o 'FIN'): ")
            
            if message.upper() == 'FIN':
                break
            
            if not message.strip():
                continue
            
            # Parsear mensaje
            trade_data = self.parse_telegram_message(message)
            
            if trade_data:
                # Agregar a Google Sheets
                if self.add_trade_to_sheets(trade_data):
                    trades_imported += 1
                else:
                    print("❌ Error agregando trade a Google Sheets")
            else:
                print("❌ No se pudo parsear el mensaje")
        
        print(f"\n✅ Importación completada: {trades_imported} trades importados")
    
    def import_sample_data(self):
        """Importar datos de muestra basados en el reporte"""
        print("📊 IMPORTANDO DATOS DE MUESTRA")
        print("=" * 50)
        
        # Datos basados en el reporte que viste
        sample_trades = [
            {
                'timestamp': (datetime.now() - timedelta(days=1, hours=2)).isoformat(),
                'symbol': 'BTCUSDT',
                'side': 'SELL',
                'price': 118723.77,
                'amount': 10.0,
                'result': 'PÉRDIDA',
                'pnl': -0.28,
                'capital': 57.17
            },
            {
                'timestamp': (datetime.now() - timedelta(days=1, hours=1)).isoformat(),
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'price': 113191.27,
                'amount': 10.0,
                'result': 'PÉRDIDA',
                'pnl': -0.79,
                'capital': 55.58
            }
        ]
        
        trades_imported = 0
        for trade in sample_trades:
            if self.add_trade_to_sheets(trade):
                trades_imported += 1
        
        print(f"✅ Datos de muestra importados: {trades_imported} trades")

def main():
    """Función principal"""
    importer = TelegramTradeImporter()
    
    print("🤖 IMPORTADOR DE OPERACIONES DE TELEGRAM")
    print("=" * 50)
    print("1. Importar desde mensajes de Telegram")
    print("2. Importar datos de muestra")
    print("3. Salir")
    
    choice = input("\nSelecciona una opción (1-3): ")
    
    if choice == "1":
        importer.import_from_manual_data()
    elif choice == "2":
        importer.import_sample_data()
    elif choice == "3":
        print("👋 ¡Hasta luego!")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
