#!/usr/bin/env python3
"""
🔍 Test de Google Sheets
Verifica si Google Sheets está funcionando correctamente
"""

import os
import sys
from datetime import datetime

def test_google_sheets():
    """Probar Google Sheets"""
    
    print("🔍 TEST DE GOOGLE SHEETS")
    print("=" * 40)
    
    # 1. Verificar credentials.json
    print("1️⃣ Verificando credentials.json...")
    if os.path.exists('credentials.json'):
        print("✅ credentials.json encontrado")
        print(f"   Tamaño: {os.path.getsize('credentials.json')} bytes")
    else:
        print("❌ credentials.json NO encontrado")
        return False
    
    # 2. Verificar dependencias
    print("\n2️⃣ Verificando dependencias...")
    try:
        import gspread
        print("✅ gspread instalado")
    except ImportError:
        print("❌ gspread NO instalado")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google-auth instalado")
    except ImportError:
        print("❌ google-auth NO instalado")
        return False
    
    # 3. Probar conexión
    print("\n3️⃣ Probando conexión...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        print("✅ Conexión exitosa")
        
        # 4. Probar acceso a spreadsheet
        print("\n4️⃣ Probando acceso a spreadsheet...")
        try:
            spreadsheet = client.open("Trading Bot Log")
            print("✅ Spreadsheet 'Trading Bot Log' encontrado")
            
            try:
                worksheet = spreadsheet.worksheet("Trading Log")
                print("✅ Worksheet 'Trading Log' encontrado")
                
                # 5. Probar escritura
                print("\n5️⃣ Probando escritura...")
                test_data = [
                    datetime.now().strftime("%Y-%m-%d\t%H:%M:%S"),
                    "TEST",
                    "BUY",
                    "$100,000.00",
                    "10",
                    "test",
                    "100%",
                    "TEST - Verificación de conexión",
                    "TEST",
                    "$0.00",
                    "100.00"
                ]
                
                worksheet.append_row(test_data)
                print("✅ Escritura exitosa")
                
                # Limpiar fila de test
                worksheet.delete_rows(len(worksheet.get_all_values()))
                print("✅ Limpieza completada")
                
                return True
                
            except gspread.WorksheetNotFound:
                print("❌ Worksheet 'Trading Log' NO encontrado")
                return False
                
        except gspread.SpreadsheetNotFound:
            print("❌ Spreadsheet 'Trading Bot Log' NO encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    success = test_google_sheets()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 GOOGLE SHEETS FUNCIONANDO CORRECTAMENTE")
        print("✅ El bot debería poder registrar operaciones")
    else:
        print("❌ GOOGLE SHEETS NO FUNCIONA")
        print("🔧 Revisar configuración")

if __name__ == "__main__":
    main()
