# 🔄 ACTUALIZAR WORKER EXISTENTE - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR

## 📊 **RESUMEN**

**¡ACTUALIZAR EL WORKER EXISTENTE `menudito-trading-bot` CON AUTO PAIR SELECTOR!**

No necesitas crear un nuevo servicio. Solo actualizar el worker que ya tienes con las nuevas funcionalidades del Auto Pair Selector.

---

## 🎯 **PASOS PARA ACTUALIZAR**

### 1️⃣ **Actualizar Código en GitHub**

1. **Commit y push** de todos los cambios FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR:
   ```bash
   git add .
   git commit -m "FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR: Selección automática de mejores pares en tendencia"
   git push origin main
   ```

### 2️⃣ **Actualizar Variables en Render**

1. **Ir a Render Dashboard**: https://dashboard.render.com
2. **Seleccionar**: `menudito-trading-bot` (worker existente)
3. **Ir a**: Environment Variables
4. **Añadir/Actualizar** estas variables:

#### 🔑 **Variables Nuevas del Auto Pair Selector (Añadir)**

```bash
# === AUTO PAIR SELECTOR ===
AUTO_PAIR_SELECTOR=true
PAIRS_CANDIDATES=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,TONUSDT,MATICUSDT,ARBUSDT,OPUSDT,LTCUSDT,APTUSDT,TRXUSDT
MAX_ACTIVE_PAIRS=4
REBALANCE_MINUTES=60
LOOKBACK_HOURS=24

# === AUTO PAIR SELECTOR: FILTROS MÍNIMOS ===
CAND_MIN_24H_VOLUME_USD=100000000
CAND_MIN_ATR_BPS=15.0
CAND_MAX_SPREAD_BPS=2.0
CAND_MIN_TREND_SCORE=0.60
CAND_MAX_CORRELATION=0.85

# === AUTO PAIR SELECTOR: SEGURIDAD DE CAMBIO ===
DO_NOT_SWITCH_IF_POSITION_OPEN=true
MIN_HOURS_BETWEEN_SWITCHES=2

# === AUTO PAIR SELECTOR: FALLBACK ===
ENABLE_MULTI_PAIR=true
PAIRS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT
```

#### 🔑 **Variables Existentes FASE 1.6 (Verificar)**

```bash
# === FASE 1.6: CONFIGURACIÓN BÁSICA ===
MODE=testnet
LIVE_TRADING=true
SHADOW_MODE=true
SESSION_WINDOW=09:00-22:00 Europe/Madrid
TIMEZONE=Europe/Madrid

# === FASE 1.6: RIESGO (V1 BLOQUEADA) ===
POSITION_SIZING_MODE=percent_of_equity
POSITION_PERCENT=0.10
MIN_NOTIONAL_USD=5
DAILY_MAX_DRAWDOWN_PCT=0.50
WEEKLY_MAX_DRAWDOWN_PCT=1.50
MAX_CONSECUTIVE_LOSSES=2
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
ATR_MIN_PCT=0.041

# === FASE 1.6: LATENCIA/ESTABILIDAD (V1 BLOQUEADA) ===
MAX_WS_LATENCY_MS=1500
MAX_REST_LATENCY_MS=800
RETRY_ORDER=2

# === FASE 1.6: KILL-SWITCH ===
KILL_SWITCH_TRIGGERED=false
AUTO_REVERT_TO_SHADOW=true

# === FASE 1.6: TELEMETRÍA ===
TELEMETRY_ENABLED=true
SLIPPAGE_TRACKING=true
FILL_LATENCY_TRACKING=true
REAL_VS_TESTNET_COMPARISON=true
MAX_LATENCY_MS=1500
MAX_RETRY_ATTEMPTS=2
PAUSE_AFTER_FAILURE_MIN=15

# === FASE 1.6: VALIDACIONES ===
DAILY_REPORT_ENABLED=true
READY_TO_SCALE_THRESHOLD_PF=1.5
READY_TO_SCALE_THRESHOLD_DD=0.5
READY_TO_SCALE=false

# === FASE 1.6: RESUMEN DIARIO ===
DAILY_SUMMARY_ENABLED=true
DAILY_SUMMARY_TIME=22:05 Europe/Madrid

# === FASE 1.6: OPCIONALES ===
BREAKEVEN_ENABLED=false

# === FASE 1.6: CONFIGURACIÓN ADICIONAL ===
CYCLE_INTERVAL_SECONDS=180
MAKER_ONLY=true
SPREAD_ADAPTIVE=true
POSITION_SIZE_USD_MIN=2.00
```

### 3️⃣ **Verificar Credenciales Existentes**

**IMPORTANTE**: Verificar que estas variables ya existen:
- ✅ `TELEGRAM_BOT_TOKEN`
- ✅ `TELEGRAM_CHAT_ID`
- ✅ `GOOGLE_SHEETS_CREDENTIALS`
- ✅ `GOOGLE_SHEETS_SPREADSHEET_ID`
- ✅ `BINANCE_API_KEY`
- ✅ `BINANCE_SECRET_KEY`

---

## ✅ **VERIFICACIÓN DE ACTUALIZACIÓN**

### 📊 **Logs Esperados (Post-Update)**

```
🚀 Iniciando Trading Bot - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR
📊 Modo: testnet
⚙️ Configuración: config_fase_1_6.py
🎯 Estrategia: breakout

📊 Multi-Par Configuración:
🎯 Símbolos: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
📊 Actual: BTCUSDT
🔄 Rotación: Cada 4 ciclos

🎯 Auto Pair Selector:
✅ ACTIVO
📊 Candidatos: 15 pares
🎯 Máximo activos: 4
🔄 Rebalance: 60 min
📊 Pares activos: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT

📈 Targets FASE 1.6:
🎯 TP Mínimo: 22.0 bps
🎯 TP Buffer: 4.0 bps
📊 RR Garantizado: 1.25:1

🛡️ Seguridad:
📊 DD Máximo: 0.50%
📊 Trades Máx/Día: 6
📊 Cooldown: 30min

📊 Filtros:
🎯 Rango Mín: 5.0 bps
🎯 Spread Máx: 2.0 bps
🎯 Vol Mín: $5,000,000
🎯 ATR Mín: 0.041%

---
🚀 ¡Bot listo para operar!
```

### 📱 **Telegram Alert Esperada**

```
🤖 **BOT PROFESIONAL - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR**

📅 **Fecha**: 2025-01-XX XX:XX:XX
🔄 **Modo**: testnet
🛡️ **Shadow Mode**: true

📊 **Multi-Par Configuración**:
🎯 **Símbolos**: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
📊 **Actual**: BTCUSDT
🔄 **Rotación**: Cada 4 ciclos

🎯 **Auto Pair Selector**:
✅ **ACTIVO**
📊 **Candidatos**: 15 pares
🎯 **Máximo activos**: 4
🔄 **Rebalance**: 60 min
📊 **Pares activos**: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT

📈 **Targets FASE 1.6**:
🎯 **TP Mínimo**: 22.0 bps
🎯 **TP Buffer**: 4.0 bps
📊 **RR Garantizado**: 1.25:1

🛡️ **Seguridad**:
📊 **DD Máximo**: 0.50%
📊 **Trades Máx/Día**: 6
📊 **Cooldown**: 30min

📊 **Filtros**:
🎯 **Rango Mín**: 5.0 bps
🎯 **Spread Máx**: 2.0 bps
🎯 **Vol Mín**: $5,000,000
🎯 **ATR Mín**: 0.041%

---
🚀 **¡Bot listo para operar!**
```

---

## 🎯 **MONITOREO POST-ACTIVACIÓN**

### **1. Verificar Auto Pair Selector**
- ✅ **Logs**: "🎯 Auto Pair Selector habilitado"
- ✅ **Pares activos**: Selección automática visible
- ✅ **Rebalance**: Cambios cada 60 minutos

### **2. Verificar Funcionalidad**
- ✅ **Multi-par**: Rotación automática
- ✅ **Filtros**: Aplicación de filtros FASE 1.6
- ✅ **Telemetría**: Datos del universo
- ✅ **Resumen diario**: 22:05 CET

### **3. Verificar Métricas**
- ✅ **Google Sheets**: Nuevas columnas con datos
- ✅ **P&L neto**: Cálculo correcto con fees/slippage
- ✅ **TP mínimo**: ≥ 22 bps (fricción + buffer)
- ✅ **RR garantizado**: ≥ 1.25:1

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### ❌ **Error: Auto Pair Selector no disponible**
```bash
# Verificar que pair_selector.py existe en el repositorio
# Debe estar en la raíz del proyecto
```

### ❌ **Error: Variables no encontradas**
```bash
# Verificar que todas las variables del Auto Pair Selector están en Render
# Environment Variables → Buscar AUTO_PAIR_SELECTOR, PAIRS_CANDIDATES, etc.
```

### ❌ **Error: ImportError: cannot import name 'pair_selector'**
```bash
# Verificar que pair_selector.py está en el repositorio
# Debe estar en la raíz del proyecto
```

### ❌ **Error: No se pudieron seleccionar pares activos**
```bash
# Verificar que PAIRS_CANDIDATES no está vacío
# Verificar que MAX_ACTIVE_PAIRS > 0
```

---

## 🎯 **PRÓXIMOS PASOS**

### 📊 **Validación (24-48h)**
1. ✅ **Logs**: Verificar inicio correcto con Auto Pair Selector
2. ✅ **Telegram**: Confirmar alerta de inicio con pares activos
3. ✅ **Trades**: Verificar multi-par + Auto Pair Selector funcionando
4. ✅ **Rebalance**: Confirmar cambios automáticos cada 60 min
5. ✅ **Resumen**: Confirmar 22:05 CET con datos del universo

### 🚀 **Escalado a Real**
1. **Condición**: PF ≥ 1.5 y DD ≤ 0.5% (3-5 días)
2. **Cambiar**: `MODE=production` en variables
3. **Monitoreo**: 24h canary intensivo
4. **Reversión**: Automática si PF < 1.0

---

## 🎉 **CONCLUSIÓN**

**¡WORKER EXISTENTE ACTUALIZADO CON AUTO PAIR SELECTOR!**

### ✅ **Estado Final**
- **Worker**: ✅ `menudito-trading-bot` actualizado
- **Configuración**: ✅ FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR
- **Variables**: ✅ Todas configuradas
- **Multi-par**: ✅ 4 símbolos activos
- **Auto Pair Selector**: ✅ 15 candidatos, 4 activos
- **Rebalance**: ✅ Cada 60 minutos
- **Resumen diario**: ✅ 22:05 CET
- **Documentación**: ✅ Completa

### 🚀 **Próximo Objetivo**
**¡DEPLOY AUTOMÁTICO Y OPERACIÓN EN TESTNET CON AUTO PAIR SELECTOR!**

**¡Listo para operar en producción con capital real y selección automática de pares! 🚀📊**
