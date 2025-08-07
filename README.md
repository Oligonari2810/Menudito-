# 🤖 Trading Bot Survivor - $50 → $1000

## 🎯 **OBJETIVO**
Bot de trading automatizado diseñado para convertir **$50 en $1000** en 25 días usando estrategias de supervivencia ultra-optimizadas.

## 🚀 **CARACTERÍSTICAS PRINCIPALES**

### ✅ **Funcionalidades Core:**
- **🔄 Trading automatizado** 24/7 en Binance Testnet
- **🧠 Validación con IA** (OpenAI GPT-3.5)
- **📱 Alertas Telegram** en tiempo real
- **📊 Logging en Google Sheets** completo
- **🛡️ Gestión de riesgo** inteligente
- **🌐 Despliegue autónomo** en Render

### 🎯 **Estrategia Survivor:**
- **💰 Capital diario**: 60% ($30.00)
- **🛡️ Capital protegido**: 40%
- **📊 Operaciones/día**: 15 máximo
- **🎯 Confianza mínima**: 10%
- **⚡ Take profit**: 4.2%
- **🛑 Stop loss**: 0.7%
- **📈 Apalancamiento**: 3x

## 🛠️ **INSTALACIÓN LOCAL**

### 📋 **Requisitos:**
```bash
Python 3.9+
Git
Cuenta en Binance Testnet
Bot de Telegram
API Key de OpenAI
Google Sheets API
```

### 🔧 **Configuración:**

1. **📥 Clonar repositorio:**
```bash
git clone https://github.com/Oligonari2810/Menudito.git
cd Menudito
```

2. **📦 Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **🔑 Configurar variables de entorno:**
```bash
# Crear archivo .env
cp .env.example .env

# Editar .env con tus API keys:
BINANCE_API_KEY=tu_api_key_binance_testnet
BINANCE_SECRET_KEY=tu_secret_key_binance_testnet
TELEGRAM_BOT_TOKEN=tu_bot_token_telegram
TELEGRAM_CHAT_ID=tu_chat_id_telegram
OPENAI_API_KEY=tu_api_key_openai
```

4. **🚀 Ejecutar bot:**
```bash
python3 main_survivor.py --strategy breakout
```

## ☁️ **DESPLIEGUE AUTÓNOMO EN RENDER**

### 🌐 **Ventajas del despliegue en la nube:**
- **🔄 Ejecución 24/7** sin ordenador
- **🛡️ Reinicio automático** si se detiene
- **📊 Health checks** para monitoreo
- **📱 Alertas automáticas** por Telegram
- **💾 Logs persistentes** en la nube

### 🚀 **Pasos para desplegar:**

1. **📤 Subir a GitHub:**
```bash
git add .
git commit -m "🚀 Bot de trading survivor listo para despliegue"
git push origin main
```

2. **🌐 Conectar con Render:**
   - Ve a [render.com](https://render.com)
   - Crea cuenta y conecta tu repositorio
   - Render detectará automáticamente `render.yaml`

3. **🔑 Configurar variables en Render:**
```env
BINANCE_API_KEY=tu_api_key_binance_testnet
BINANCE_SECRET_KEY=tu_secret_key_binance_testnet
TELEGRAM_BOT_TOKEN=tu_bot_token_telegram
TELEGRAM_CHAT_ID=tu_chat_id_telegram
OPENAI_API_KEY=tu_api_key_openai
GOOGLE_SHEETS_CREDENTIALS=tu_credencial_google_sheets
RENDER_URL=https://tu-app.onrender.com
```

### 📊 **Monitoreo en Render:**
- **🌐 Health check**: `https://tu-app.onrender.com/health`
- **📊 Estado del bot**: `https://tu-app.onrender.com/`
- **🔄 Reinicio manual**: `https://tu-app.onrender.com/restart`

## 📊 **ESTRUCTURA DEL PROYECTO**

```
Menudito/
├── 🤖 main_survivor.py          # Bot principal
├── ⚙️ config_survivor_final.py   # Configuración final
├── 📊 sheets_logger.py           # Google Sheets
├── 🌐 deploy_render.py           # Servidor Render
├── 📈 daily_evaluation.py        # Reportes diarios
├── ⚙️ render.yaml               # Configuración Render
├── 📦 modules/                   # Módulos del sistema
│   ├── ai_validator.py          # Validación IA
│   ├── binance_client.py        # Cliente Binance
│   ├── telegram_alert.py        # Alertas Telegram
│   ├── trading_logic.py         # Lógica de trading
│   ├── logger.py                # Sistema de logs
│   └── config.py                # Configuración base
└── 📋 requirements.txt           # Dependencias
```

## 🎯 **ESTRATEGIA DE TRADING**

### 🛡️ **Modo Survivor (Actual):**
- **🎯 Objetivo**: Proteger capital mientras se busca crecimiento
- **💰 Capital diario**: 60% del total
- **📊 Operaciones**: Máximo 15 por día
- **🎯 Confianza**: Mínimo 10%
- **⚡ Take profit**: 4.2%
- **🛑 Stop loss**: 0.7%

### 🚀 **Transición automática:**
- **🔄 Cambio a modo agresivo** cuando capital ≥ $60
- **📈 Parámetros agresivos** automáticos
- **📱 Notificación Telegram** al cambiar

### 🧠 **Validación con IA:**
- **✅ CONFIRMADO**: Ejecutar operación
- **❌ RECHAZADO**: No ejecutar
- **⚠️ CAUTELA**: Ejecutar con precaución (si confianza ≥ 15%)

## 📱 **ALERTAS Y MONITOREO**

### 📱 **Alertas Telegram:**
- **🚀 Inicio del bot**
- **📊 Señales de trading**
- **💰 Operaciones ejecutadas**
- **🔄 Reinicios automáticos**
- **❌ Errores críticos**
- **📈 Cambios de modo**
- **📊 Reportes diarios**

### 📊 **Google Sheets:**
- **📋 Auditoría completa** de todas las operaciones
- **📈 P&L en tiempo real**
- **🎯 Progreso vs objetivo**
- **📊 Análisis de rendimiento**
- **🛡️ Gestión de riesgo**

## 🛡️ **GESTIÓN DE RIESGO**

### ✅ **Protecciones implementadas:**
- **💰 Límite de capital diario** (60%)
- **🛑 Stop loss automático** (0.7%)
- **⚡ Take profit** (4.2%)
- **🔄 Reinicio automático** si se detiene
- **📊 Health checks** cada minuto
- **🛡️ Bloqueo diario** tras pérdida >15%

### 🚨 **Alertas críticas:**
- **❌ Error de conexión**: Reinicio automático
- **❌ API errors**: Logging y alertas
- **❌ Memory issues**: Limpieza automática
- **❌ Timeout errors**: Reintentos inteligentes

## 📈 **EVALUACIÓN DIARIA**

### 🕐 **Reporte automático:**
- **⏰ Horario**: Todos los días a las 00:00
- **📊 Contenido**: Estado completo del bot
- **📱 Envío**: Telegram automático
- **💾 Log**: Archivo persistente

### 📋 **Métricas evaluadas:**
- **🤖 Estado del bot** (running/stopped)
- **🔄 Número de reinicios**
- **📊 Progreso vs objetivo**
- **🛡️ Configuración activa**
- **💡 Recomendaciones**

## 💰 **COSTOS Y RECURSOS**

### 💵 **Render (Recomendado):**
- **💰 Plan Starter**: $7/mes
- **🕐 Uptime**: 99.9%
- **💾 RAM**: 512MB
- **⚡ CPU**: Compartido
- **🌐 Banda ancha**: Ilimitada

### 🔧 **Recursos necesarios:**
- **📊 Binance Testnet**: Gratuito
- **🧠 OpenAI API**: ~$5-10/mes
- **📱 Telegram Bot**: Gratuito
- **📊 Google Sheets**: Gratuito

## 🚨 **ADVERTENCIAS IMPORTANTES**

### ⚠️ **Antes de usar:**
1. **🔑 Verificar API keys** en variables de entorno
2. **📊 Probar en testnet** antes de usar real
3. **📱 Configurar Telegram** correctamente
4. **💾 Verificar Google Sheets** credentials
5. **🛡️ Revisar límites** de APIs

### 🛡️ **Monitoreo recomendado:**
- **📱 Revisar alertas Telegram** diariamente
- **📊 Verificar Google Sheets** semanalmente
- **🌐 Health checks** automáticos
- **📈 Reportes diarios** automáticos

## 🎯 **OBJETIVO FINAL**

### ✅ **Resultado esperado:**
- **💰 Capital inicial**: $50.00
- **🎯 Capital objetivo**: $1000.00
- **📅 Tiempo**: 25 días
- **📈 Retorno requerido**: 1900%
- **📊 Retorno diario promedio**: 15%

### 🚀 **Ventajas del sistema:**
- **🔄 Ejecución 24/7** sin intervención
- **📊 Monitoreo automático** completo
- **🛡️ Protección contra fallos**
- **📱 Alertas en tiempo real**
- **💾 Logs persistentes**
- **🌐 Acceso web** para control

## 📞 **SOPORTE**

### 🔧 **Si tienes problemas:**
1. **📱 Revisar alertas Telegram**
2. **🌐 Verificar health checks**
3. **📊 Revisar logs en Render**
4. **🔄 Reiniciar manualmente** si es necesario

### 📚 **Documentación adicional:**
- **📖 Configuración detallada**: Ver `config_survivor_final.py`
- **🌐 Despliegue Render**: Ver `render.yaml`
- **📊 Monitoreo**: Ver `deploy_render.py`

---

## 🎉 **¡EL BOT ESTÁ LISTO PARA OPERAR DE FORMA COMPLETAMENTE AUTÓNOMA!**

**Desarrollado con ❤️ para maximizar la probabilidad de éxito en el objetivo $50 → $1000** 