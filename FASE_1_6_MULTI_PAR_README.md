# 🚀 FASE 1.6 MULTI-PAR - DOCUMENTACIÓN COMPLETA

## 📊 **RESUMEN EJECUTIVO**

**FASE 1.6 MULTI-PAR** es la implementación final y bloqueada del bot de trading profesional, con las siguientes características principales:

- ✅ **Multi-Par**: 4 símbolos (BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT)
- ✅ **Configuración V1 Bloqueada**: Parámetros optimizados y fijos
- ✅ **Rotación Automática**: Cada 4 ciclos
- ✅ **Resumen Diario**: Telegram a las 22:05 CET
- ✅ **P&L Neto Real**: Con fees + slippage
- ✅ **TP/SL Dinámicos**: TP ≥ 22 bps, RR 1.25:1 garantizado
- ✅ **Filtros Avanzados**: Rango, spread, volumen, latencia
- ✅ **Gestión de Riesgo**: Kill-switches automáticos

---

## 🎯 **CONFIGURACIÓN V1 BLOQUEADA**

### 📊 **Multi-Par**
```python
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
ROTATION_CYCLES = 4  # Rotación cada 4 ciclos
```

### 🎯 **Targets de Salida**
```python
TP_MIN_BPS = 22.0        # TP mínimo bloqueado
TP_BUFFER_BPS = 4.0      # Buffer bloqueado
RR_GUARANTEED = 1.25     # RR garantizado siempre
```

### 🛡️ **Gestión de Riesgo**
```python
POSITION_PERCENT = 0.10   # 0.10% del equity
MAX_TRADES_PER_DAY = 6    # Máximo 6 trades/día
DAILY_MAX_DRAWDOWN_PCT = 0.50  # 0.5% máximo
COOLDOWN_AFTER_LOSS_MIN = 30   # 30 min cooldown
```

### 📊 **Filtros de Entrada**
```python
MIN_RANGE_BPS = 5.0       # Rango mínimo 5 bps
MAX_SPREAD_BPS = 2.0      # Spread máximo 2 bps
MIN_VOL_USD = 5000000     # Volumen mínimo $5M
ATR_MIN_PCT = 0.041       # ATR mínimo 0.041%
```

### ⚡ **Latencia/Estabilidad**
```python
MAX_WS_LATENCY_MS = 1500  # WebSocket ≤ 1500ms
MAX_REST_LATENCY_MS = 800 # REST ≤ 800ms
RETRY_ORDER = 2           # 2 reintentos
```

---

## 🔄 **FUNCIONAMIENTO MULTI-PAR**

### 📊 **Rotación de Símbolos**
1. **Ciclo 1-4**: BTCUSDT
2. **Ciclo 5-8**: ETHUSDT
3. **Ciclo 9-12**: BNBUSDT
4. **Ciclo 13-16**: SOLUSDT
5. **Ciclo 17+**: Vuelve a BTCUSDT

### 💰 **Precios Simulados por Símbolo**
- **BTCUSDT**: $40,000 - $50,000
- **ETHUSDT**: $2,000 - $3,000
- **BNBUSDT**: $500 - $650
- **SOLUSDT**: $80 - $120

### 🎯 **Targets por Símbolo**
Cada símbolo mantiene los mismos targets FASE 1.6:
- **TP**: ≥ 22 bps (dinámico según ATR)
- **SL**: TP/1.25 (RR garantizado)
- **Filtros**: Aplicados uniformemente

---

## 📊 **RESUMEN DIARIO**

### 🕐 **Horario**
- **Hora**: 22:05 CET (Europe/Madrid)
- **Frecuencia**: Diario
- **Formato**: Telegram Markdown

### 📈 **Métricas Incluidas**
```markdown
📊 **RESUMEN DIARIO - FASE 1.6 MULTI-PAR**

📅 **Fecha**: 2025-01-XX
🕐 **Hora**: 22:05:XX

💰 **Capital**: $XX.XX
📈 **P&L Neto Día**: $X.XXXX

📊 **Métricas**:
🎯 **Trades**: X
✅ **Ganados**: X
📊 **Win Rate**: XX.X%
📈 **Profit Factor**: X.XX
📉 **Drawdown**: X.XX%

🔄 **Multi-Par**:
📊 **Símbolos**: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
🎯 **Actual**: XXXX
🔄 **Rotaciones**: X

🛡️ **Seguridad**:
📊 **DD Máximo**: 0.50%
📊 **Trades Máx/Día**: 6
📊 **TP Mínimo**: 22.0 bps
```

---

## 🛡️ **GESTIÓN DE RIESGO**

### 🚨 **Kill-Switches Automáticos**
1. **DD Diario ≥ 0.5%**: Pausa automática
2. **DD Semanal ≥ 1.5%**: Pausa automática
3. **Pérdidas Consecutivas ≥ 2**: Cooldown 30min
4. **Trades/Día ≥ 6**: Pausa hasta siguiente día

### 🔄 **Auto-Reversión**
- **Trigger**: Cualquier kill-switch
- **Acción**: `LIVE_TRADING=false`, `SHADOW_MODE=true`
- **Alerta**: Telegram inmediata
- **Log**: Google Sheets

---

## 📊 **MÉTRICAS Y TELEMETRÍA**

### 🎯 **Métricas por Trade**
```python
# Nuevas métricas FASE 1.6
'tp_bps': 22.0,           # TP en bps
'sl_bps': 17.6,           # SL en bps
'rr_ratio': 1.25,         # Risk-Reward ratio
'fric_bps': 16.5,         # Fricción total
'tp_floor': 18.5,         # TP mínimo requerido
'fees_bps': 7.5,          # Fees en bps
'slippage_bps': 1.5,      # Slippage en bps
'range_bps': 15.2,        # Rango en bps
'spread_bps': 1.8,        # Spread en bps
'atr_pct': 0.85,          # ATR en %
'friction_impact': 0.77,  # Impacto fricción (77%)
```

### 📈 **P&L Neto Real**
```python
# Cálculo P&L neto
pnl_bruto = exit_price - entry_price
fees_cost = notional * (fee_taker + fee_maker)
slippage_cost = notional * slippage_bps / 10000
pnl_neto = pnl_bruto - fees_cost - slippage_cost
```

---

## 🚀 **DEPLOYMENT**

### 📋 **Requisitos**
1. **Python 3.8+**
2. **Dependencias**: `requirements.txt`
3. **Configuración**: `config_fase_1_6.py`
4. **Variables de entorno**: `fase_1_6_env.txt`

### 🔧 **Instalación**
```bash
# Clonar repositorio
git clone <repository>
cd Menudito-

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp fase_1_6_env.txt .env
# Editar .env con credenciales reales

# Verificar configuración
python verify_multi_par_config.py
```

### 🚀 **Ejecución**
```bash
# Modo testnet
python minimal_working_bot.py --mode=testnet

# Modo producción
python minimal_working_bot.py --mode=production
```

---

## 📊 **MONITOREO Y ALERTAS**

### 📱 **Telegram**
- ✅ Alertas de trades en tiempo real
- ✅ Resumen diario a las 22:05 CET
- ✅ Kill-switches automáticos
- ✅ Estado del bot

### 📊 **Google Sheets**
- ✅ Registro completo de trades
- ✅ Métricas FASE 1.6
- ✅ Telemetría avanzada
- ✅ Historial de sesiones

### 📈 **Logs**
- ✅ Logging detallado
- ✅ Rotación automática
- ✅ Archivos de sesión
- ✅ Debugging completo

---

## 🎯 **OBJETIVOS DE RENDIMIENTO**

### 📊 **Métricas Objetivo (3-5 días)**
- **Win Rate**: ≥ 50%
- **Profit Factor**: ≥ 1.5
- **Drawdown Día**: ≤ 0.5%
- **Drawdown 5d**: ≤ 1.5%
- **TP Floor Compliance**: ≥ 95%

### 🚀 **Escalado a Real**
- **Condición**: PF ≥ 1.5 y DD ≤ 0.5%
- **Capital**: Micro ($2-5 por trade)
- **Duración**: 24-48h canary
- **Reversión**: Automática si PF < 1.0

---

## 🔧 **MANTENIMIENTO**

### 📊 **Verificación Diaria**
1. **Logs**: Revisar errores
2. **Métricas**: Win Rate, PF, DD
3. **Telegram**: Alertas y resúmenes
4. **Sheets**: Datos completos

### 🔄 **Actualizaciones**
- **Configuración**: Solo cambios críticos
- **Código**: Solo hotfixes
- **Deployment**: Automático en Render
- **Backup**: Estado guardado

---

## 📞 **SOPORTE**

### 🆘 **Problemas Comunes**
1. **Credenciales**: Verificar .env
2. **Sheets**: Verificar credentials.json
3. **Telegram**: Verificar bot token
4. **Latencia**: Revisar logs

### 📧 **Contacto**
- **Issues**: GitHub
- **Logs**: Render dashboard
- **Alertas**: Telegram automático

---

## 🎉 **CONCLUSIÓN**

**FASE 1.6 MULTI-PAR** representa la versión final y optimizada del bot de trading, con:

- ✅ **Configuración bloqueada** y probada
- ✅ **Multi-par** para diversificación
- ✅ **Gestión de riesgo** robusta
- ✅ **Telemetría completa** y real
- ✅ **Resúmenes automáticos** diarios
- ✅ **Escalabilidad** a producción

**¡Listo para operar en producción con capital real! 🚀**
