#!/usr/bin/env python3
"""
📊 Script para importar una operación específica a Google Sheets
"""

import os
from datetime import datetime

def import_single_trade():
    """Importar operación específica a Google Sheets"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Configurar credenciales
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        if os.path.exists('credentials.json'):
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            print("✅ Google Sheets configurado correctamente")
        else:
            print("❌ credentials.json no encontrado")
            return
        
        # Datos de la operación
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'BTCUSDT',
            'side': 'SELL',
            'price': 113736.54,
            'amount': 10.0,
            'result': 'PÉRDIDA',
            'pnl': -0.11,
            'capital': 48.50
        }
        
        # Abrir spreadsheet
        spreadsheet_name = "Trading Bot Log"
        worksheet_name = "Trading Log"
        
        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(spreadsheet_name)
            print(f"✅ Spreadsheet creado: {spreadsheet_name}")
        
        # Abrir worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
            headers = ['Timestamp', 'Symbol', 'Side', 'Price', 'Amount', 'Result', 'P&L', 'Capital']
            worksheet.append_row(headers)
            print(f"✅ Worksheet creado: {worksheet_name}")
        
        # Preparar datos
        row_data = [
            trade_data['timestamp'],
            trade_data['symbol'],
            trade_data['side'],
            trade_data['price'],
            trade_data['amount'],
            trade_data['result'],
            trade_data['pnl'],
            trade_data['capital']
        ]
        
        # Agregar fila
        worksheet.append_row(row_data)
        print(f"✅ Trade importado: {trade_data['side']} {trade_data['symbol']} @ ${trade_data['price']:,.2f}")
        print(f"📊 Resultado: {trade_data['result']} (${trade_data['pnl']:.2f})")
        print(f"🏦 Capital: ${trade_data['capital']:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("📊 IMPORTANDO OPERACIÓN ESPECÍFICA")
    print("=" * 50)
    import_single_trade()
