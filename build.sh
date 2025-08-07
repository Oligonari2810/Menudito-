#!/bin/bash
# Script de build para Python 3.9

echo "🔧 Forzando Python 3.9.18..."

# Verificar versión de Python
python --version

# Actualizar pip
python -m pip install --upgrade pip

# Instalar setuptools y wheel para Python 3.9
pip install setuptools>=65.0.0 wheel>=0.40.0

# Instalar todas las dependencias
pip install -r requirements.txt

echo "✅ Build completado exitosamente con Python 3.9"
