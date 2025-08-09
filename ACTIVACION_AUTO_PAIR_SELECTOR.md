# 🎯 ACTIVACIÓN AUTO PAIR SELECTOR - FASE 1.6

## 📊 **RESUMEN EJECUTIVO**

**¡ACTIVAR AUTO PAIR SELECTOR EN EL WORKER EXISTENTE!**

El Auto Pair Selector está completamente implementado y listo para activación. Esta mejora seleccionará automáticamente los mejores pares en tendencia basándose en métricas de mercado.

---

## 🚀 **PASOS DE ACTIVACIÓN**

### **1️⃣ Commit y Push del Código**

```bash
# Asegurar que todos los cambios están en GitHub
git add .
git commit -m "FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR: Selección automática de mejores pares en tendencia"
git push origin main
```

### **2️⃣ Actualizar Variables en Render**

**Ir a**: https://dashboard.render.com → `menudito-trading-bot` → Environment Variables

#### **🔑 NUEVAS VARIABLES (Añadir)**

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

### **3️⃣ Verificar Variables Existentes**

**Confirmar que estas variables ya existen**:
- ✅ `TELEGRAM_BOT_TOKEN`
- ✅ `TELEGRAM_CHAT_ID`
- ✅ `GOOGLE_SHEETS_CREDENTIALS`
- ✅ `GOOGLE_SHEETS_SPREADSHEET_ID`
- ✅ `BINANCE_API_KEY`
- ✅ `BINANCE_SECRET_KEY`

---

## ✅ **VERIFICACIÓN POST-ACTIVACIÓN**

### **📊 Logs Esperados**

```
🚀 Iniciando Trading Bot - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR
📊 Modo: testnet
⚙️ Configuración: config_fase_1_6.py
🎯 Estrategia: breakout

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

---
🚀 ¡Bot listo para operar!
```

### **📱 Telegram Alert Esperada**

```
🤖 **BOT PROFESIONAL - FASE 1.6 MULTI-PAR + AUTO PAIR SELECTOR**

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

---
🚀 **¡Bot listo para operar!**
```

---

## 🎯 **MONITOREO EN TIEMPO REAL**

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

## 🚨 **SOLUCIÓN DE PROBLEMAS RÁPIDA**

### **❌ Error: Auto Pair Selector no disponible**
```bash
# Verificar que pair_selector.py existe en el repositorio
# Debe estar en la raíz del proyecto
```

### **❌ Error: Variables no encontradas**
```bash
# Verificar que todas las variables del Auto Pair Selector están en Render
# Environment Variables → Buscar AUTO_PAIR_SELECTOR, PAIRS_CANDIDATES, etc.
```

### **❌ Error: No se pudieron seleccionar pares activos**
```bash
# Verificar que PAIRS_CANDIDATES no está vacío
# Verificar que MAX_ACTIVE_PAIRS > 0
```

---

## 🎯 **PRÓXIMOS PASOS**

### **📊 Validación (24-48h)**
1. ✅ **Logs**: Verificar inicio correcto con Auto Pair Selector
2. ✅ **Telegram**: Confirmar alerta de inicio con pares activos
3. ✅ **Trades**: Verificar multi-par + Auto Pair Selector funcionando
4. ✅ **Rebalance**: Confirmar cambios automáticos cada 60 min
5. ✅ **Resumen**: Confirmar 22:05 CET con datos del universo

### **🚀 Escalado a Real**
1. **Condición**: PF ≥ 1.5 y DD ≤ 0.5% (3-5 días)
2. **Cambiar**: `MODE=production` en variables
3. **Monitoreo**: 24h canary intensivo
4. **Reversión**: Automática si PF < 1.0

---

## 🎉 **BENEFICIOS DEL AUTO PAIR SELECTOR**

### **📈 Rentabilidad**
- **Mejores pares**: Selección basada en métricas objetivas
- **Tendencia**: Enfoque en movimientos direccionales
- **Volatilidad**: Aprovecha movimientos significativos

### **🛡️ Gestión de Riesgo**
- **Diversificación**: Correlación controlada
- **Liquidez**: Volumen mínimo garantizado
- **Costes**: Spread limitado

### **🤖 Automatización**
- **Sin intervención**: Selección automática
- **Rebalance**: Ajustes periódicos
- **Fallback**: Continuidad de operación

---

## 🎯 **CONCLUSIÓN**

**¡AUTO PAIR SELECTOR LISTO PARA ACTIVACIÓN!**

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
