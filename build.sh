#!/bin/bash
# Script de build para Python 3.9

echo "🔧 Iniciando build con Python 3.9..."

# Actualizar pip
python -m pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt

echo "✅ Build completado exitosamente"
