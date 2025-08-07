#!/usr/bin/env python3
"""
📊 LOGGING MEJORADO - Solo archivo y consola
Sistema de logging optimizado sin CSV automático
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
# import pandas as pd  # Removido para compatibilidad con plan gratuito
from modules.config import TradingConfig

class TradingLogger:
    """Logger optimizado para el bot de trading"""
    
    def __init__(self):
        self.config = TradingConfig()
        
        # Configurar logging
        self._setup_logging()
        
        # Historial de operaciones en memoria
        self.trades_history = []
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        try:
            # Crear directorio de logs si no existe
            log_dir = os.path.dirname(self.config.LOGGING['file_path'])
            os.makedirs(log_dir, exist_ok=True)
            
            # Configurar logger
            self.logger = logging.getLogger('trading_bot_enhanced')
            self.logger.setLevel(self.config.LOGGING['level'])
            
            # Evitar duplicación de handlers
            if not self.logger.handlers:
                # Handler para archivo
                file_handler = logging.FileHandler(self.config.LOGGING['file_path'])
                file_handler.setLevel(self.config.LOGGING['level'])
                
                # Handler para consola
                console_handler = logging.StreamHandler()
                console_handler.setLevel(self.config.LOGGING['level'])
                
                # Formato
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                # Agregar handlers
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
            
            self.logger.info("✅ Sistema de logging inicializado")
            
        except Exception as e:
            print(f"❌ Error configurando logging: {e}")
    
    def log_signal(self, signal: Dict):
        """Registrar señal de trading"""
        try:
            # Validar campos requeridos
            required_fields = ['signal', 'reason', 'confidence']
            for field in required_fields:
                if field not in signal:
                    self.logger.error(f"Campo requerido '{field}' no encontrado en señal")
                    return
            
            self.logger.info(f"📊 SEÑAL: {signal['signal']} - {signal['reason']} (Confianza: {signal['confidence']:.1f}%)")
        except Exception as e:
            self.logger.error(f"Error registrando señal: {e}")
    
    def log_trade(self, trade: Dict):
        """Registrar operación ejecutada"""
        try:
            # Validar campos requeridos
            required_fields = ['side', 'quantity', 'symbol', 'price', 'amount']
            for field in required_fields:
                if field not in trade:
                    self.logger.error(f"Campo requerido '{field}' no encontrado en trade")
                    return
            
            # Agregar a historial en memoria
            self.trades_history.append(trade)
            
            # Log detallado
            self.logger.info(f"💰 TRADE: {trade['side']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:,.2f} (${trade['amount']:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error registrando operación: {e}")
    
    def log_ai_validation(self, signal: Dict, ai_response: Dict):
        """Registrar validación de IA"""
        try:
            status = ai_response.get('ai_response', 'N/A')
            confidence_adjusted = ai_response.get('confidence', signal['confidence'])
            reasoning = ai_response.get('reason', 'Sin validación')
            
            # Validar que la respuesta de IA no sea vacía
            if not status or status == 'N/A':
                status = 'CAUTELA'
                reasoning = 'Sin respuesta de IA - usando fallback'
                confidence_adjusted = signal['confidence']
            
            self.logger.info(f"🧠 IA: {status}")
            self.logger.info(f"{reasoning} (Confianza ajustada: {confidence_adjusted:.1%})")
            
        except Exception as e:
            self.logger.error(f"Error registrando validación IA: {e}")
    
    def log_error(self, error: str, context: str = ""):
        """Registrar error"""
        try:
            if context:
                self.logger.error(f"❌ {context}: {error}")
            else:
                self.logger.error(f"❌ {error}")
        except Exception as e:
            print(f"Error en logging: {e}")
    
    def log_warning(self, warning: str):
        """Registrar advertencia"""
        try:
            self.logger.warning(f"⚠️ {warning}")
        except Exception as e:
            print(f"Error en logging: {e}")
    
    def log_info(self, message: str):
        """Registrar información"""
        try:
            self.logger.info(message)
        except Exception as e:
            print(f"Error en logging: {e}")
    
    def get_trades_history(self) -> List[Dict]:
        """Obtener historial de operaciones desde memoria"""
        return self.trades_history.copy()
    
    def get_trades_dataframe(self) -> Optional[Dict]:
        """Obtener datos como diccionario (sin pandas)"""
        try:
            if not self.trades_history:
                return None
            
            # Retornar como diccionario simple
            return {
                'trades': self.trades_history,
                'count': len(self.trades_history),
                'total_trades': len(self.trades_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando historial: {e}")
            return None
    
    def generate_daily_summary(self) -> Dict:
        """Generar resumen diario"""
        try:
            trades_data = self.get_trades_dataframe()
            if trades_data is None or not trades_data['trades']:
                return {
                    'total_trades': 0,
                    'total_pnl': 0.0,
                    'win_rate': 0.0,
                    'avg_pnl': 0.0
                }
            
            # Filtrar por fecha actual
            today = datetime.now().date()
            today_trades = []
            for trade in trades_data['trades']:
                if 'timestamp' in trade:
                    trade_date = datetime.fromisoformat(trade['timestamp']).date()
                    if trade_date == today:
                        today_trades.append(trade)
            
            if not today_trades:
                return {
                    'total_trades': 0,
                    'total_pnl': 0.0,
                    'win_rate': 0.0,
                    'avg_pnl': 0.0
                }
            
            # Calcular métricas
            total_trades = len(today_trades)
            total_pnl = sum(trade.get('pnl', 0) for trade in today_trades)
            winning_trades = len([t for t in today_trades if t.get('pnl', 0) > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'avg_pnl': avg_pnl
            }
            
        except Exception as e:
            self.logger.error(f"Error generando resumen diario: {e}")
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'avg_pnl': 0.0
            }
    
    def generate_performance_report(self) -> Dict:
        """Generar reporte de rendimiento completo"""
        try:
            trades_data = self.get_trades_dataframe()
            if trades_data is None or not trades_data['trades']:
                return {
                    'total_trades': 0,
                    'total_pnl': 0.0,
                    'win_rate': 0.0,
                    'avg_pnl': 0.0,
                    'best_trade': 0.0,
                    'worst_trade': 0.0,
                    'trades_by_strategy': {},
                    'trades_by_direction': {}
                }
            
            trades = trades_data['trades']
            
            # Métricas básicas
            total_trades = len(trades)
            total_pnl = sum(trade.get('pnl', 0) for trade in trades)
            winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            # Mejor y peor operación
            pnls = [trade.get('pnl', 0) for trade in trades]
            best_trade = max(pnls) if pnls else 0
            worst_trade = min(pnls) if pnls else 0
            
            # Operaciones por estrategia
            trades_by_strategy = df['strategy'].value_counts().to_dict() if 'strategy' in df.columns else {}
            
            # Operaciones por dirección
            trades_by_direction = df['side'].value_counts().to_dict() if 'side' in df.columns else {}
            
            return {
                'total_trades': total_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'avg_pnl': avg_pnl,
                'best_trade': best_trade,
                'worst_trade': worst_trade,
                'trades_by_strategy': trades_by_strategy,
                'trades_by_direction': trades_by_direction
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de rendimiento: {e}")
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'trades_by_strategy': {},
                'trades_by_direction': {}
            } 