# 🎯 AUTO PAIR SELECTOR - FASE 1.6

## 📊 **RESUMEN EJECUTIVO**

El **Auto Pair Selector** es una mejora inteligente para FASE 1.6 que selecciona automáticamente los mejores pares en tendencia basándose en métricas de mercado como volumen, volatilidad, spread y tendencia.

---

## 🎯 **CARACTERÍSTICAS PRINCIPALES**

### ✅ **Selección Automática de Pares**
- **15 candidatos**: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, LINKUSDT, TONUSDT, MATICUSDT, ARBUSDT, OPUSDT, LTCUSDT, APTUSDT, TRXUSDT
- **4 pares activos**: Selecciona los mejores según score
- **Rebalance automático**: Cada 60 minutos (configurable)

### 📊 **Métricas de Selección**
```python
score = 0.35 * volume_rank +
        0.25 * norm(atr_bps) +
        0.25 * trend_score +
        0.10 * norm(range_bps) -
        0.15 * norm(spread_bps)
```

### 🛡️ **Filtros de Seguridad**
- **Volumen mínimo**: ≥ 100M USD 24h
- **ATR mínimo**: ≥ 15 bps (0.15%)
- **Spread máximo**: ≤ 2 bps (0.02%)
- **Trend score mínimo**: ≥ 0.6
- **Correlación máxima**: ≤ 0.85

### 🔄 **Sistema de Rebalance**
- **Frecuencia**: 60 minutos (configurable)
- **Protección**: No cambia pares con posiciones abiertas
- **Tiempo mínimo**: 2 horas entre switches
- **Fallback**: Usa pares por defecto si falla

---

## 🔧 **CONFIGURACIÓN**

### **Variables de Entorno**

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

---

## 🎯 **FUNCIONAMIENTO**

### **1. Selección Inicial**
```python
# Al iniciar el bot
active_pairs = pair_selector.select_active_pairs()
# Resultado: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
```

### **2. Cálculo de Scores**
```python
# Para cada candidato
for symbol in candidates:
    # Obtener datos OHLCV
    df = get_market_data(symbol, '1h', 24)
    
    # Calcular métricas
    volume_24h = df['volume'].sum()
    atr_bps = calculate_atr(df) / price * 10000
    trend_score = calculate_trend_score(df)
    range_bps = (high - low) / close * 10000
    spread_bps = (ask - bid) / mid * 10000
    
    # Aplicar score
    score = 0.35*volume_rank + 0.25*norm(atr_bps) + 0.25*trend_score + 0.10*norm(range_bps) - 0.15*norm(spread_bps)
```

### **3. Rebalance Automático**
```python
# Cada 60 minutos
if should_rebalance():
    new_pairs = select_active_pairs()
    if new_pairs != current_pairs:
        rebalance_pairs()
```

### **4. Protección de Posiciones**
```python
# No cambiar si hay posición abierta
if position_open and do_not_switch_if_position_open:
    keep_current_pair()
```

---

## 📊 **MÉTRICAS CALCULADAS**

### **Volume Rank**
- Ranking por volumen 24h dentro de candidatos
- Normalizado: 0.3 - 1.0

### **ATR (Average True Range)**
- Volatilidad medida en bps
- Mínimo: 15 bps (0.15%)

### **Trend Score**
```python
trend_score = 0.0
# Alineación alcista: EMA20 > EMA50 > EMA100
if ema20 > ema50 > ema100:
    trend_score += 0.4
# Pendiente de regresión lineal
slope_norm = min(abs(slope) / price * 100, 1.0)
trend_score += slope_norm * 0.3
# Bonus por volatilidad
if atr_pct > 0.5:
    trend_score += 0.3
```

### **Range**
- Rango 24h en bps
- Normalizado: 20 - 200 bps

### **Spread**
- Spread bid-ask en bps
- Máximo: 2 bps (0.02%)

---

## 🛡️ **SEGURIDAD Y PROTECCIONES**

### **Filtros Mínimos**
- **Volumen**: ≥ 100M USD (liquidez)
- **ATR**: ≥ 15 bps (volatilidad)
- **Spread**: ≤ 2 bps (coste)
- **Trend**: ≥ 0.6 (tendencia)

### **Protección de Cambios**
- **Posiciones abiertas**: No cambiar
- **Tiempo mínimo**: 2 horas entre switches
- **Correlación**: ≤ 0.85 (diversificación)

### **Fallback**
- **Error en datos**: Usar pares por defecto
- **Sin candidatos**: Usar configuración original
- **Timeout**: Continuar con pares actuales

---

## 📈 **TELEMETRÍA**

### **Datos del Universo**
```python
universe_data = {
    'timestamp': '2025-01-09T12:00:00',
    'pair': 'BTCUSDT',
    'score': 0.85,
    'vol_usd_24h': 1500000000,
    'atr_bps': 25.5,
    'range_bps': 45.2,
    'spread_bps': 1.2,
    'trend_score': 0.75,
    'corr_max': 0.45,
    'active': True
}
```

### **Logs Detallados**
```
📊 RESUMEN DEL UNIVERSO:
==================================================
🏆 TOP 5 CANDIDATOS:
1. BTCUSDT: 0.85 | Vol: $1500.0M | ATR: 25.5bps | Trend: 0.75 | ✅ ACTIVO
2. ETHUSDT: 0.72 | Vol: $800.0M | ATR: 18.2bps | Trend: 0.65 | ✅ ACTIVO
3. SOLUSDT: 0.68 | Vol: $300.0M | ATR: 35.1bps | Trend: 0.80 | ✅ ACTIVO
4. BNBUSDT: 0.65 | Vol: $500.0M | ATR: 22.3bps | Trend: 0.60 | ✅ ACTIVO
5. XRPUSDT: 0.58 | Vol: $200.0M | ATR: 12.5bps | Trend: 0.45 | ⏳ CANDIDATO
==================================================
```

---

## 🚀 **INTEGRACIÓN CON EL BOT**

### **Inicialización**
```python
# En ProfessionalTradingBot.__init__()
if self.auto_pair_selector and AUTO_PAIR_SELECTOR_AVAILABLE:
    self.pair_selector = init_pair_selector(config)
    self.active_pairs = self.initialize_active_pairs()
```

### **Ciclo de Trading**
```python
# En run_trading_cycle()
if self.should_rebalance_pairs():
    if self.rebalance_pairs():
        self.logger.info("✅ Rebalance completado")
```

### **Selección de Símbolos**
```python
# En simulate_trading_signal()
if self.auto_pair_selector and self.pair_selector and self.active_pairs:
    current_symbol = random.choice(self.active_pairs)
else:
    current_symbol = self.get_current_symbol()
```

---

## 🧪 **TESTS Y VALIDACIÓN**

### **Script de Prueba**
```bash
python3 test_auto_pair_selector.py
```

### **Tests Incluidos**
1. ✅ **Configuración**: Variables de entorno
2. ✅ **Inicialización**: Auto Pair Selector
3. ✅ **Selección**: Pares activos
4. ✅ **Scores**: Cálculo de métricas
5. ✅ **Rebalance**: Verificación de cambios
6. ✅ **Universo**: Datos y telemetría

### **Resultados Esperados**
```
🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!
✅ Auto Pair Selector listo para producción

🎯 CARACTERÍSTICAS VERIFICADAS:
📊 Selección automática de pares
🎯 Cálculo de scores basado en métricas
🔄 Sistema de rebalance
📈 Filtros de mercado
🛡️ Seguridad de cambio
📊 Telemetría del universo
```

---

## 📊 **VENTAJAS**

### **Rentabilidad**
- **Mejores pares**: Selección basada en métricas objetivas
- **Tendencia**: Enfoque en movimientos direccionales
- **Volatilidad**: Aprovecha movimientos significativos

### **Gestión de Riesgo**
- **Diversificación**: Correlación controlada
- **Liquidez**: Volumen mínimo garantizado
- **Costes**: Spread limitado

### **Automatización**
- **Sin intervención**: Selección automática
- **Rebalance**: Ajustes periódicos
- **Fallback**: Continuidad de operación

---

## 🎯 **PRÓXIMOS PASOS**

### **1. Activación**
```bash
# En Render - Environment Variables
AUTO_PAIR_SELECTOR=true
PAIRS_CANDIDATES=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,TONUSDT,MATICUSDT,ARBUSDT,OPUSDT,LTCUSDT,APTUSDT,TRXUSDT
MAX_ACTIVE_PAIRS=4
REBALANCE_MINUTES=60
```

### **2. Monitoreo**
- **Logs**: Verificar selección de pares
- **Telemetría**: Revisar scores y métricas
- **Rebalance**: Confirmar cambios automáticos

### **3. Optimización**
- **Ajustar filtros**: Según resultados
- **Frecuencia**: Rebalance más/menos frecuente
- **Candidatos**: Añadir/quitar pares

---

## 🎉 **CONCLUSIÓN**

El **Auto Pair Selector** representa una mejora significativa para FASE 1.6, proporcionando:

- ✅ **Selección inteligente** de pares en tendencia
- ✅ **Gestión automática** de la cartera
- ✅ **Protección robusta** contra cambios innecesarios
- ✅ **Telemetría completa** del universo de pares
- ✅ **Integración perfecta** con el bot existente

**¡Listo para activar y operar en producción! 🚀📊**
