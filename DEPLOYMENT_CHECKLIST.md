# 🚀 CHECKLIST DE DESPLIEGUE FASE 1.6

## 📋 Pre-despliegue

### ✅ 1. Fix de Imports
- [ ] **NameError corregido**: `from typing import Any, Dict, List, Optional`
- [ ] **Firmas de funciones**: `Dict[str, Any]` en lugar de `Dict`
- [ ] **Test de imports**: `python3 test_typing_imports.py`

### ✅ 2. Configuración FASE 1.6
- [ ] **Variables de entorno**: Todas las variables FASE 1.6 definidas
- [ ] **Configuración centralizada**: `config_fase_1_6.py` creado
- [ ] **Validación de config**: `python3 test_config_validation.py`
- [ ] **TP mínimo > fricción**: `TP_MIN_BPS >= tp_floor`

### ✅ 3. Tests de Validación
- [ ] **Tests FASE 1.6**: `python3 test_fase_1_6.py` (5/5 passed)
- [ ] **Tests de imports**: `python3 test_typing_imports.py`
- [ ] **Tests de config**: `python3 test_config_validation.py`
- [ ] **Todos los tests pasan**: Sin errores ni warnings

## 🔧 Despliegue

### ✅ 4. Build y Deploy
- [ ] **Git commit**: Cambios subidos a GitHub
- [ ] **Render build**: Build exitoso sin errores
- [ ] **Deploy automático**: Bot actualizado en Render
- [ ] **Logs de inicio**: Mensaje "FASE 1.6" en logs

### ✅ 5. Validación Post-despliegue
- [ ] **Bot iniciado**: Logs muestran "Bot profesional - FASE 1.6"
- [ ] **Configuración cargada**: Variables FASE 1.6 aplicadas
- [ ] **Primer ciclo**: Trade ejecutado con métricas FASE 1.6
- [ ] **Telegram alertas**: Mensajes incluyen TP/SL/RR

## 📊 Monitoreo

### ✅ 6. Métricas FASE 1.6
- [ ] **Google Sheets**: Nuevas columnas con datos
  - [ ] `TP (bps)` | `SL (bps)` | `Range (bps)` | `Spread (bps)`
  - [ ] `Fee (bps)` | `Est. Fee (USD)` | `Slippage (bps)`
  - [ ] `PnL Bruto (USD)` | `PnL Neto (USD)` | `RR` | `ATR (%)`
- [ ] **P&L neto**: `pnl_neto < pnl_bruto` (incluye fees/slippage)
- [ ] **TP mínimo**: `TP (bps) >= 18.5` (fricción + buffer)
- [ ] **RR garantizado**: `RR >= 1.25` en todos los trades

### ✅ 7. Filtros de Mercado
- [ ] **Filtros aplicados**: Logs muestran "Filtros pasados" o "rechazado"
- [ ] **Rango mínimo**: Trades rechazados si `range_bps < 5.0`
- [ ] **Spread máximo**: Trades rechazados si `spread_bps > 2.0`
- [ ] **Volumen mínimo**: Trades rechazados si `vol_usd < 5000000`
- [ ] **Latencia**: Trades rechazados si latencia > límites

### ✅ 8. Kill-switches
- [ ] **Límites configurados**: 
  - [ ] `DAILY_MAX_DRAWDOWN_PCT=0.50`
  - [ ] `MAX_CONSECUTIVE_LOSSES=2`
  - [ ] `MAX_TRADES_PER_DAY=8`
- [ ] **Auto-reversión**: `SHADOW_MODE=true` al disparar límite
- [ ] **Alertas Telegram**: Notificación cuando se dispara kill-switch

## 🎯 Objetivos de Rendimiento

### ✅ 9. Métricas de Éxito (24-48h)
- [ ] **Profit Factor ≥ 1.5**: En testnet después de 24-48h
- [ ] **Win Rate ≥ 50%**: Mantener consistencia
- [ ] **Drawdown ≤ 0.5%**: Protección de capital
- [ ] **Friction Impact ≤ 20%**: Fees + slippage controlados
- [ ] **RR ≥ 1.25**: Ratio riesgo-recompensa garantizado

### ✅ 10. Estabilidad
- [ ] **Sin errores**: No hay excepciones no manejadas
- [ ] **Latencia bajo control**: REST < 800ms, WS < 1500ms
- [ ] **Uptime**: Bot funcionando 24/7 sin interrupciones
- [ ] **Logs limpios**: Sin warnings o errores críticos

## 🔍 Troubleshooting

### ❌ Problemas Comunes

**TP muy bajo:**
```bash
# Aumentar TP_MIN_BPS
TP_MIN_BPS=25.0  # 0.25% mínimo
```

**Filtros muy estrictos:**
```bash
# Ajustar filtros
MIN_RANGE_BPS=3.0   # Más permisivo
MAX_SPREAD_BPS=3.0  # Más permisivo
```

**Latencia alta:**
```bash
# Aumentar límites
MAX_REST_LATENCY_MS=1000
MAX_WS_LATENCY_MS=2000
```

**NameError con typing:**
```bash
# Verificar imports
python3 test_typing_imports.py
```

### 📊 Logs de Debug

```bash
# Ver logs FASE 1.6
tail -f minimal_working_bot.py | grep "FASE 1.6"

# Ver filtros aplicados
tail -f minimal_working_bot.py | grep "Filtros"

# Ver TP/SL calculados
tail -f minimal_working_bot.py | grep "TP="
```

## 🎉 Criterios de Éxito

### ✅ Despliegue Exitoso
- [ ] **Build OK**: Sin errores de compilación
- [ ] **Tests verdes**: Todos los tests pasan
- [ ] **Config válida**: TP mínimo > fricción
- [ ] **Bot operativo**: Funcionando en Render

### ✅ Funcionalidad FASE 1.6
- [ ] **TP mínimo garantizado**: `tp_bps >= tp_floor`
- [ ] **Filtros activos**: Rechazan condiciones desfavorables
- [ ] **P&L neto**: Cálculo correcto con fees/slippage
- [ ] **Telemetría**: Nuevas columnas en Sheets
- [ ] **Alertas mejoradas**: Telegram con métricas FASE 1.6

### ✅ Rendimiento Objetivo
- [ ] **PF ≥ 1.5**: Después de 24-48h de operación
- [ ] **DD ≤ 0.5%**: Protección de capital mantenida
- [ ] **WR ≥ 50%**: Consistencia en win rate
- [ ] **Estabilidad**: Sin errores críticos

---

## 📝 Notas de Despliegue

**Fecha de despliegue:** [FECHA]
**Versión:** FASE 1.6
**Responsable:** [NOMBRE]
**Estado:** ✅ COMPLETADO / ❌ PENDIENTE

### 🔄 Próximos Pasos
1. **Monitorear** logs de Render por 24h
2. **Verificar** métricas en Google Sheets
3. **Evaluar** rendimiento después de 48h
4. **Ajustar** parámetros si es necesario
5. **Escalar** a producción si objetivos cumplidos

---

**🚀 ¡FASE 1.6 LISTA PARA PRODUCCIÓN!**
