#!/usr/bin/env python3
"""
🔧 Convertir credentials.json a variable de entorno
Para usar en Render
"""

import json
import os

def convert_credentials_to_env():
    """Convertir credentials.json a formato de variable de entorno"""
    
    print("🔧 CONVERTIR CREDENCIALES A VARIABLE DE ENTORNO")
    print("=" * 50)
    
    # Leer credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json no encontrado")
        return
    
    try:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
        
        # Convertir a string JSON
        credentials_json = json.dumps(credentials)
        
        print("✅ Credenciales leídas correctamente")
        print(f"📏 Tamaño: {len(credentials_json)} caracteres")
        
        # Mostrar variable de entorno
        print("\n📋 VARIABLE DE ENTORNO PARA RENDER:")
        print("=" * 40)
        print("GOOGLE_SHEETS_CREDENTIALS=" + credentials_json)
        
        # Guardar en archivo
        with open('google_sheets_env.txt', 'w') as f:
            f.write("GOOGLE_SHEETS_CREDENTIALS=" + credentials_json)
        
        print("\n✅ Guardado en google_sheets_env.txt")
        print("📋 Copia esta variable a Render:")
        print("  1. Ve a tu proyecto en Render")
        print("  2. Environment Variables")
        print("  3. Agrega: GOOGLE_SHEETS_CREDENTIALS")
        print("  4. Pega el valor completo")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    convert_credentials_to_env()
