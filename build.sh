#!/bin/bash
# Script de build personalizado para Render

echo "🔧 Iniciando build personalizado..."

# Actualizar pip
python -m pip install --upgrade pip

# Instalar setuptools y wheel primero
pip install setuptools>=65.0.0 wheel>=0.40.0

# Instalar dependencias básicas
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install schedule==1.2.0
pip install numpy==1.24.3

# Instalar dependencias de APIs
pip install python-binance==1.0.19
pip install ccxt==4.1.77
pip install python-telegram-bot==20.7
pip install openai==1.3.0

# Instalar dependencias web
pip install flask==2.3.3

# Instalar dependencias de Google
pip install gspread==5.12.0
pip install google-auth==2.23.4
pip install google-auth-oauthlib==1.1.0
pip install google-auth-httplib2==0.1.1

echo "✅ Build completado exitosamente"
