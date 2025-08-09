# 🤖 Trading Bot Professional - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR

## 🚀 **Bot de Trading Autónomo como Worker en Render**

### ✅ **Estado Actual:**
- **Deployment**: Worker (sin servicio web)
- **Status**: ✅ Funcionando 24/7
- **Telegram**: ✅ Alertas en tiempo real
- **Capital**: $55.58 (+11.16% desde $50)
- **Operaciones**: 74 trades ejecutados
- **FASE 1.6**: ✅ Implementada con Auto Pair Selector

---

## 📋 **Configuración Requerida**

### 🔑 **Google Sheets Setup**

Para que el bot registre operaciones en Google Sheets, necesitas:

1. **📁 Archivo credentials.json**
   - Descarga desde Google Cloud Console
   - Colócalo en la raíz del proyecto
   - Nombre exacto: `credentials.json`

2. **📊 Spreadsheet**
   - Nombre: "Trading Bot Log"
   - Hoja: "Trading Log"
   - Se creará automáticamente si no existe

### 📱 **Variables de Entorno (Render)**
```bash
# === FASE 1.6: CONFIGURACIÓN BÁSICA ===
MODE=testnet
LIVE_TRADING=true
SHADOW_MODE=true
SESSION_WINDOW=09:00-22:00 Europe/Madrid
TIMEZONE=Europe/Madrid

# === AUTO PAIR SELECTOR ===
AUTO_PAIR_SELECTOR=true
PAIRS_CANDIDATES=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,TONUSDT,MATICUSDT,ARBUSDT,OPUSDT,LTCUSDT,APTUSDT,TRXUSDT
MAX_ACTIVE_PAIRS=4
REBALANCE_MINUTES=60
LOOKBACK_HOURS=24

# === AUTO PAIR SELECTOR: FILTROS MÍNIMOS ===
CAND_MIN_24H_VOLUME_USD=100000000
CAND_MIN_ATR_BPS=12.0
CAND_MAX_SPREAD_BPS=2.0
CAND_MIN_TREND_SCORE=0.60
CAND_MAX_CORRELATION=0.85

# === AUTO PAIR SELECTOR: SEGURIDAD DE CAMBIO ===
DO_NOT_SWITCH_IF_POSITION_OPEN=true
MIN_HOURS_BETWEEN_SWITCHES=2

# === AUTO PAIR SELECTOR: FALLBACK ===
ENABLE_MULTI_PAIR=true
PAIRS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT

# === FASE 1.6: RIESGO (V1 BLOQUEADA) ===
POSITION_PERCENT=0.10
DAILY_MAX_DRAWDOWN_PCT=0.50
MAX_TRADES_PER_DAY=6
COOLDOWN_AFTER_LOSS_MIN=30

# === FASE 1.6: FEES/SLIPPAGE (V1 BLOQUEADA) ===
FEE_TAKER_BPS=7.5
FEE_MAKER_BPS=2.0
SLIPPAGE_BPS=1.5
TP_BUFFER_BPS=4.0

# === FASE 1.6: OBJETIVOS DE SALIDA (V1 BLOQUEADA) ===
TP_MODE=fixed_min
TP_MIN_BPS=22.0
ATR_PERIOD=14
TP_ATR_MULT=0.50
SL_ATR_MULT=0.40

# === FASE 1.6: FILTROS DE ENTRADA (V1 BLOQUEADA) ===
MIN_RANGE_BPS=5.0
MAX_SPREAD_BPS=2.0
MIN_VOL_USD=5000000
ATR_MIN_PCT=0.033

# === CREDENCIALES ===
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
GOOGLE_SHEETS_CREDENTIALS=tu_google_sheets_credentials
GOOGLE_SHEETS_SPREADSHEET_ID=tu_spreadsheet_id
```

---

## 🎯 **Características del Bot**

### 🎯 **Auto Pair Selector:**
- **15 candidatos**: Selección automática de mejores pares
- **4 pares activos**: Máximo simultáneo
- **Rebalance**: Cada 60 minutos
- **Filtros**: Volumen, ATR, spread, tendencia
- **Protección**: No cambia con posiciones abiertas

### ⚡ **Optimizado para Plan Gratuito:**
- **Ciclos**: Cada 180 segundos
- **Señales**: Multi-par + Auto Pair Selector
- **Alertas**: Cada operación
- **Reportes**: Diario a las 22:05 CET
- **Reinicios**: Máximo 10 intentos

### 📊 **FASE 1.6 - Métricas Avanzadas:**
- **TP mínimo**: 22 bps (fricción + buffer)
- **RR garantizado**: ≥ 1.25:1
- **P&L neto**: Con fees + slippage
- **Filtros**: Rango, spread, volumen, latencia

### 🛡️ **Gestión de Riesgo:**
- **Capital protegido**: 0.50% DD máximo
- **Stop loss**: Dinámico (TP/1.25)
- **Take profit**: Mínimo 22 bps
- **Máximo trades/día**: 6

---

## 📈 **Monitoreo en Tiempo Real**

### 📱 **Telegram:**
- ✅ Alertas de operaciones con Auto Pair Selector
- ✅ Reportes diarios automáticos
- ✅ Estado del bot y pares activos
- ✅ Métricas de rendimiento FASE 1.6

### 🌐 **Render Dashboard:**
- ✅ Health checks
- ✅ Logs detallados con Auto Pair Selector
- ✅ Estado del servicio
- ✅ Métricas de uso

### 📊 **Google Sheets:**
- ✅ Registro de todas las operaciones
- ✅ Nuevas columnas FASE 1.6: TP/SL, fees, P&L neto
- ✅ Datos del universo de pares
- ✅ Historial completo

---

## 🔧 **Despliegue Local**

```bash
# Clonar repositorio
git clone https://github.com/Oligonari2810/Menudito-.git
cd Menudito$$

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar bot
python3 minimal_working_bot.py --mode=testnet
```

---

## 📊 **Métricas Actuales**

### 💰 **Rendimiento:**
- **Capital inicial**: $50.00
- **Capital actual**: $55.58
- **Ganancia total**: +$5.58 (+11.16%)
- **Operaciones**: 74 trades
- **Ciclos**: 240 ejecutados

### 🎯 **Auto Pair Selector:**
- **Pares activos**: 4 seleccionados automáticamente
- **Rebalance**: Cada 60 minutos
- **Candidatos**: 15 pares disponibles
- **Filtros aplicados**: Volumen, ATR, spread, tendencia

### 📈 **FASE 1.6:**
- ✅ **TP mínimo**: ≥ 22 bps (fricción + buffer)
- ✅ **RR garantizado**: ≥ 1.25:1
- ✅ **P&L neto**: Con fees + slippage
- ✅ **Filtros**: Aplicados correctamente

---

## 🎯 **Archivos Principales**

### 📁 **Core Files:**
- `minimal_working_bot.py` - Bot principal FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR
- `config_fase_1_6.py` - Configuración centralizada
- `pair_selector.py` - Auto Pair Selector
- `test_auto_pair_selector.py` - Tests del selector

### 📁 **Documentación:**
- `AUTO_PAIR_SELECTOR_README.md` - Documentación completa del selector
- `ACTUALIZAR_WORKER_EXISTENTE.md` - Guía de actualización
- `ACTIVACION_AUTO_PAIR_SELECTOR.md` - Guía de activación

### 📁 **Configuración:**
- `render.yaml` - Configuración Render
- `fase_1_6_env.txt` - Variables de entorno
- `requirements.txt` - Dependencias

---

## 🎉 **¡Éxito Total!**

**El bot está funcionando de manera completamente autónoma en Render con todas las optimizaciones aplicadas para el plan gratuito y el nuevo Auto Pair Selector implementado.**

**¡Disfruta de tu bot de trading 24/7 con selección automática de pares!** 🚀📈 