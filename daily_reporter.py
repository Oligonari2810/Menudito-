#!/usr/bin/env python3
"""
📊 DAILY REPORTER - SISTEMA DE REPORTE FIN DE DÍA
Resumen diario de WinRate, PF, DD y evaluación para escalar
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class DailyReporter:
    """Sistema de reporte fin de día"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuración de umbrales
        self.READY_TO_SCALE_THRESHOLD_PF = 1.5
        self.READY_TO_SCALE_THRESHOLD_DD = 0.5
        
        # Historial de reportes
        self.daily_reports = []
        self.current_day_data = {
            'trades': [],
            'pnl_data': [],
            'errors': [],
            'start_time': None,
            'end_time': None
        }
        
        # Estado de escalado
        self.ready_to_scale = False
        self.scale_recommendation = None
        
    def start_daily_session(self):
        """Iniciar sesión diaria"""
        self.current_day_data = {
            'trades': [],
            'pnl_data': [],
            'errors': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        self.logger.info("📊 Sesión diaria iniciada")
    
    def record_trade(self, trade_data: Dict):
        """Registrar trade en el día actual"""
        self.current_day_data['trades'].append(trade_data)
        
        # Registrar P&L si está disponible
        if 'realized_pnl' in trade_data:
            self.current_day_data['pnl_data'].append(trade_data['realized_pnl'])
    
    def record_error(self, error_data: Dict):
        """Registrar error en el día actual"""
        self.current_day_data['errors'].append(error_data)
    
    def calculate_daily_metrics(self) -> Dict:
        """Calcular métricas del día"""
        trades = self.current_day_data['trades']
        pnl_data = self.current_day_data['pnl_data']
        
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'daily_drawdown': 0.0,
                'total_pnl': 0.0,
                'error_count': len(self.current_day_data['errors'])
            }
        
        # Win Rate
        winning_trades = [t for t in trades if t.get('result', '') == 'WIN']
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0.0
        
        # Profit Factor
        gains = sum([pnl for pnl in pnl_data if pnl > 0])
        losses = abs(sum([pnl for pnl in pnl_data if pnl < 0]))
        profit_factor = gains / losses if losses > 0 else (gains if gains > 0 else 0.0)
        
        # Daily Drawdown
        if pnl_data:
            cumulative_pnl = []
            running_total = 0
            for pnl in pnl_data:
                running_total += pnl
                cumulative_pnl.append(running_total)
            
            peak = max(cumulative_pnl) if cumulative_pnl else 0
            current = cumulative_pnl[-1] if cumulative_pnl else 0
            daily_drawdown = ((peak - current) / peak * 100) if peak > 0 else 0.0
        else:
            daily_drawdown = 0.0
        
        # Total P&L
        total_pnl = sum(pnl_data)
        
        return {
            'total_trades': len(trades),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'daily_drawdown': round(daily_drawdown, 2),
            'total_pnl': round(total_pnl, 4),
            'error_count': len(self.current_day_data['errors']),
            'gains': round(gains, 4),
            'losses': round(losses, 4)
        }
    
    def check_ready_to_scale(self, metrics: Dict) -> bool:
        """Verificar si está listo para escalar"""
        pf = metrics.get('profit_factor', 0.0)
        dd = metrics.get('daily_drawdown', 0.0)
        
        ready = (pf >= self.READY_TO_SCALE_THRESHOLD_PF and 
                dd <= self.READY_TO_SCALE_THRESHOLD_DD)
        
        if ready:
            self.ready_to_scale = True
            self.scale_recommendation = {
                'ready': True,
                'reason': f"PF={pf} >= {self.READY_TO_SCALE_THRESHOLD_PF} y DD={dd}% <= {self.READY_TO_SCALE_THRESHOLD_DD}%",
                'metrics': metrics
            }
        else:
            self.scale_recommendation = {
                'ready': False,
                'reason': f"PF={pf} < {self.READY_TO_SCALE_THRESHOLD_PF} o DD={dd}% > {self.READY_TO_SCALE_THRESHOLD_DD}%",
                'metrics': metrics
            }
        
        return ready
    
    def generate_daily_report(self) -> Dict:
        """Generar reporte completo del día"""
        self.current_day_data['end_time'] = datetime.now()
        
        # Calcular métricas
        metrics = self.calculate_daily_metrics()
        
        # Verificar escalado
        ready_to_scale = self.check_ready_to_scale(metrics)
        
        # Generar reporte
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'session_start': self.current_day_data['start_time'].isoformat(),
            'session_end': self.current_day_data['end_time'].isoformat(),
            'session_duration': str(self.current_day_data['end_time'] - self.current_day_data['start_time']),
            
            # Métricas principales
            'metrics': metrics,
            
            # Análisis de escalado
            'ready_to_scale': ready_to_scale,
            'scale_recommendation': self.scale_recommendation,
            
            # Detalles de trades
            'trades_summary': {
                'total_trades': len(self.current_day_data['trades']),
                'winning_trades': len([t for t in self.current_day_data['trades'] if t.get('result') == 'WIN']),
                'losing_trades': len([t for t in self.current_day_data['trades'] if t.get('result') == 'LOSS']),
                'avg_trade_pnl': round(sum(self.current_day_data['pnl_data']) / len(self.current_day_data['pnl_data']), 4) if self.current_day_data['pnl_data'] else 0.0
            },
            
            # Errores y problemas
            'errors_summary': {
                'total_errors': len(self.current_day_data['errors']),
                'error_types': self._count_error_types(),
                'last_error': self.current_day_data['errors'][-1] if self.current_day_data['errors'] else None
            },
            
            # Recomendaciones
            'recommendations': self._generate_recommendations(metrics)
        }
        
        # Guardar reporte
        self.daily_reports.append(report)
        
        return report
    
    def _count_error_types(self) -> Dict:
        """Contar tipos de errores"""
        error_types = {}
        for error in self.current_day_data['errors']:
            error_type = error.get('error_type', 'UNKNOWN')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generar recomendaciones basadas en métricas"""
        recommendations = []
        
        pf = metrics.get('profit_factor', 0.0)
        dd = metrics.get('daily_drawdown', 0.0)
        wr = metrics.get('win_rate', 0.0)
        trades = metrics.get('total_trades', 0)
        
        # Recomendaciones de escalado
        if pf >= self.READY_TO_SCALE_THRESHOLD_PF and dd <= self.READY_TO_SCALE_THRESHOLD_DD:
            recommendations.append("✅ LISTO PARA ESCALAR: PF y DD en rangos óptimos")
        else:
            if pf < self.READY_TO_SCALE_THRESHOLD_PF:
                recommendations.append(f"⚠️ PF bajo ({pf}): Revisar estrategia de entrada/salida")
            if dd > self.READY_TO_SCALE_THRESHOLD_DD:
                recommendations.append(f"⚠️ DD alto ({dd}%): Reducir tamaño de posición")
        
        # Recomendaciones de Win Rate
        if wr < 50:
            recommendations.append("⚠️ Win Rate bajo: Revisar señales de entrada")
        elif wr > 80:
            recommendations.append("✅ Win Rate excelente: Considerar aumentar tamaño")
        
        # Recomendaciones de volumen
        if trades < 3:
            recommendations.append("⚠️ Pocos trades: Revisar condiciones de mercado")
        elif trades > 20:
            recommendations.append("⚠️ Muchos trades: Considerar filtros adicionales")
        
        return recommendations
    
    def send_daily_report_telegram(self, report: Dict):
        """Enviar reporte diario por Telegram"""
        message = f"""
📊 **REPORTE DIARIO - {report['date']}**

⏱️ **Sesión**: {report['session_duration']}
📈 **Trades**: {report['trades_summary']['total_trades']}
✅ **Wins**: {report['trades_summary']['winning_trades']}
❌ **Losses**: {report['trades_summary']['losing_trades']}

📊 **Métricas**:
• Win Rate: {report['metrics']['win_rate']}%
• Profit Factor: {report['metrics']['profit_factor']}
• Daily DD: {report['metrics']['daily_drawdown']}%
• Total P&L: ${report['metrics']['total_pnl']}

🚀 **Escalado**: {'✅ LISTO' if report['ready_to_scale'] else '❌ NO LISTO'}
📝 **Razón**: {report['scale_recommendation']['reason']}

💡 **Recomendaciones**:
{chr(10).join(['• ' + rec for rec in report['recommendations']])}
        """
        
        # Aquí iría el código para enviar por Telegram
        self.logger.info(f"Reporte diario enviado: {message}")
        return message
    
    def get_historical_summary(self, days: int = 7) -> Dict:
        """Obtener resumen histórico de los últimos días"""
        recent_reports = self.daily_reports[-days:] if self.daily_reports else []
        
        if not recent_reports:
            return {}
        
        # Calcular promedios
        avg_win_rate = sum(r['metrics']['win_rate'] for r in recent_reports) / len(recent_reports)
        avg_profit_factor = sum(r['metrics']['profit_factor'] for r in recent_reports) / len(recent_reports)
        avg_daily_dd = sum(r['metrics']['daily_drawdown'] for r in recent_reports) / len(recent_reports)
        total_trades = sum(r['metrics']['total_trades'] for r in recent_reports)
        
        return {
            'period_days': days,
            'avg_win_rate': round(avg_win_rate, 2),
            'avg_profit_factor': round(avg_profit_factor, 2),
            'avg_daily_dd': round(avg_daily_dd, 2),
            'total_trades': total_trades,
            'ready_to_scale_days': len([r for r in recent_reports if r['ready_to_scale']]),
            'reports_analyzed': len(recent_reports)
        }

# Instancia global
daily_reporter = DailyReporter()
