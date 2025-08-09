#!/usr/bin/env python3
"""
📊 ANALIZADOR DE DATOS GOOGLE SHEETS - FASE 1.6
Script para analizar los resultados del bot y generar conclusiones
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("❌ Error: gspread no instalado. Instalar con: pip install gspread google-auth")
    sys.exit(1)

class SheetsAnalyzer:
    """Analizador de datos de Google Sheets para FASE 1.6"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.sheets_enabled = False
        
        # Configurar conexión
        self._setup_connection()
    
    def _setup_logging(self):
        """Configurar logging"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _setup_connection(self):
        """Configurar conexión a Google Sheets"""
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Intentar desde archivo local
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                self.client = gspread.authorize(creds)
                self.sheets_enabled = True
                self.logger.info("✅ Google Sheets configurado desde archivo local")
            # Intentar desde variable de entorno
            elif os.getenv('GOOGLE_SHEETS_CREDENTIALS'):
                import json
                credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
                creds = Credentials.from_service_account_info(json.loads(credentials_json), scopes=scope)
                self.client = gspread.authorize(creds)
                self.sheets_enabled = True
                self.logger.info("✅ Google Sheets configurado desde variable de entorno")
            else:
                self.logger.warning("⚠️ No se encontraron credenciales de Google Sheets")
                return
            
            # Abrir spreadsheet
            self.spreadsheet = self.client.open("Trading Bot Log")
            self.worksheet = self.spreadsheet.worksheet("Trading Log")
            self.logger.info("✅ Conexión a Google Sheets establecida")
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando Google Sheets: {e}")
            self.sheets_enabled = False
    
    def get_all_data(self) -> pd.DataFrame:
        """Obtener todos los datos del worksheet"""
        if not self.sheets_enabled:
            self.logger.error("❌ Google Sheets no configurado")
            return pd.DataFrame()
        
        try:
            # Obtener todos los datos
            all_records = self.worksheet.get_all_records()
            
            if not all_records:
                self.logger.warning("⚠️ No hay datos en el worksheet")
                return pd.DataFrame()
            
            # Convertir a DataFrame
            df = pd.DataFrame(all_records)
            self.logger.info(f"✅ Datos cargados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos: {e}")
            return pd.DataFrame()
    
    def analyze_fase_1_6_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar métricas específicas de FASE 1.6"""
        if df.empty:
            return {}
        
        try:
            # Filtrar solo datos de FASE 1.6
            fase_1_6_data = df[df['Fase'] == 'FASE 1.6'].copy()
            
            if fase_1_6_data.empty:
                self.logger.warning("⚠️ No hay datos de FASE 1.6")
                return {}
            
            # Convertir columnas numéricas
            numeric_columns = [
                'TP (bps)', 'SL (bps)', 'Range (bps)', 'Spread (bps)', 
                'Fee (bps)', 'Est. Fee (USD)', 'Slippage (bps)', 
                'PnL Bruto (USD)', 'PnL Neto (USD)', 'RR', 'ATR (%)'
            ]
            
            for col in numeric_columns:
                if col in fase_1_6_data.columns:
                    fase_1_6_data[col] = pd.to_numeric(fase_1_6_data[col], errors='coerce')
            
            # Análisis de métricas
            analysis = {
                'total_trades': len(fase_1_6_data),
                'win_rate': self._calculate_win_rate(fase_1_6_data),
                'profit_factor': self._calculate_profit_factor(fase_1_6_data),
                'avg_pnl_net': fase_1_6_data['PnL Neto (USD)'].mean() if 'PnL Neto (USD)' in fase_1_6_data.columns else 0,
                'total_pnl_net': fase_1_6_data['PnL Neto (USD)'].sum() if 'PnL Neto (USD)' in fase_1_6_data.columns else 0,
                'avg_tp_bps': fase_1_6_data['TP (bps)'].mean() if 'TP (bps)' in fase_1_6_data.columns else 0,
                'avg_sl_bps': fase_1_6_data['SL (bps)'].mean() if 'SL (bps)' in fase_1_6_data.columns else 0,
                'avg_rr': fase_1_6_data['RR'].mean() if 'RR' in fase_1_6_data.columns else 0,
                'avg_friction': self._calculate_avg_friction(fase_1_6_data),
                'friction_impact': self._calculate_friction_impact(fase_1_6_data),
                'filter_effectiveness': self._analyze_filters(fase_1_6_data),
                'tp_floor_compliance': self._check_tp_floor_compliance(fase_1_6_data),
                'risk_reward_analysis': self._analyze_risk_reward(fase_1_6_data)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando métricas FASE 1.6: {e}")
            return {}
    
    def _calculate_win_rate(self, df: pd.DataFrame) -> float:
        """Calcular win rate"""
        if 'Resultado' not in df.columns:
            return 0.0
        
        wins = len(df[df['Resultado'].str.contains('GANANCIA', na=False)])
        total = len(df)
        return (wins / total * 100) if total > 0 else 0.0
    
    def _calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calcular profit factor"""
        if 'PnL Neto (USD)' not in df.columns:
            return 0.0
        
        gains = df[df['PnL Neto (USD)'] > 0]['PnL Neto (USD)'].sum()
        losses = abs(df[df['PnL Neto (USD)'] < 0]['PnL Neto (USD)'].sum())
        
        return gains / losses if losses > 0 else 0.0
    
    def _calculate_avg_friction(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcular fricción promedio"""
        friction_data = {}
        
        if 'Est. Fee (USD)' in df.columns:
            friction_data['avg_fees'] = df['Est. Fee (USD)'].mean()
        
        if 'Slippage (bps)' in df.columns:
            friction_data['avg_slippage_bps'] = df['Slippage (bps)'].mean()
        
        if 'Fee (bps)' in df.columns:
            friction_data['avg_fees_bps'] = df['Fee (bps)'].mean()
        
        return friction_data
    
    def _calculate_friction_impact(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcular impacto de la fricción"""
        if 'PnL Bruto (USD)' not in df.columns or 'PnL Neto (USD)' not in df.columns:
            return {}
        
        gross_pnl = df['PnL Bruto (USD)'].sum()
        net_pnl = df['PnL Neto (USD)'].sum()
        friction_cost = gross_pnl - net_pnl
        
        return {
            'total_friction_cost': friction_cost,
            'friction_impact_pct': (friction_cost / gross_pnl * 100) if gross_pnl > 0 else 0,
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl
        }
    
    def _analyze_filters(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar efectividad de filtros"""
        filter_analysis = {}
        
        # Analizar rangos
        if 'Range (bps)' in df.columns:
            filter_analysis['avg_range_bps'] = df['Range (bps)'].mean()
            filter_analysis['min_range_bps'] = df['Range (bps)'].min()
            filter_analysis['max_range_bps'] = df['Range (bps)'].max()
        
        # Analizar spreads
        if 'Spread (bps)' in df.columns:
            filter_analysis['avg_spread_bps'] = df['Spread (bps)'].mean()
            filter_analysis['max_spread_bps'] = df['Spread (bps)'].max()
        
        return filter_analysis
    
    def _check_tp_floor_compliance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verificar cumplimiento del TP floor"""
        if 'TP (bps)' not in df.columns:
            return {}
        
        tp_floor = 18.5  # FASE 1.6 TP floor
        compliant_trades = len(df[df['TP (bps)'] >= tp_floor])
        total_trades = len(df)
        
        return {
            'tp_floor': tp_floor,
            'compliant_trades': compliant_trades,
            'total_trades': total_trades,
            'compliance_rate': (compliant_trades / total_trades * 100) if total_trades > 0 else 0,
            'min_tp_bps': df['TP (bps)'].min(),
            'avg_tp_bps': df['TP (bps)'].mean()
        }
    
    def _analyze_risk_reward(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar ratio riesgo-recompensa"""
        if 'RR' not in df.columns:
            return {}
        
        return {
            'avg_rr': df['RR'].mean(),
            'min_rr': df['RR'].min(),
            'max_rr': df['RR'].max(),
            'rr_std': df['RR'].std(),
            'rr_above_1_25': len(df[df['RR'] >= 1.25]),
            'rr_above_1_25_pct': (len(df[df['RR'] >= 1.25]) / len(df) * 100) if len(df) > 0 else 0
        }
    
    def generate_report(self) -> str:
        """Generar reporte completo"""
        if not self.sheets_enabled:
            return "❌ Google Sheets no configurado"
        
        # Obtener datos
        df = self.get_all_data()
        if df.empty:
            return "❌ No hay datos disponibles"
        
        # Analizar FASE 1.6
        analysis = self.analyze_fase_1_6_metrics(df)
        if not analysis:
            return "❌ No hay datos de FASE 1.6"
        
        # Generar reporte
        report = f"""
📊 REPORTE FASE 1.6 - ANÁLISIS DE RESULTADOS
{'='*60}

🎯 MÉTRICAS GENERALES:
• Total de trades: {analysis['total_trades']}
• Win Rate: {analysis['win_rate']:.2f}%
• Profit Factor: {analysis['profit_factor']:.2f}
• P&L Neto Total: ${analysis['total_pnl_net']:.4f}
• P&L Neto Promedio: ${analysis['avg_pnl_net']:.4f}

📈 TARGETS FASE 1.6:
• TP Promedio: {analysis['avg_tp_bps']:.1f} bps
• SL Promedio: {analysis['avg_sl_bps']:.1f} bps
• RR Promedio: {analysis['avg_rr']:.2f}:1
• Cumplimiento TP Floor: {analysis['tp_floor_compliance']['compliance_rate']:.1f}%

💰 FRICCIÓN Y COSTOS:
• Costo Total Fricción: ${analysis['friction_impact']['total_friction_cost']:.4f}
• Impacto Fricción: {analysis['friction_impact']['friction_impact_pct']:.2f}%
• P&L Bruto: ${analysis['friction_impact']['gross_pnl']:.4f}
• P&L Neto: ${analysis['friction_impact']['net_pnl']:.4f}

🛡️ FILTROS Y RIESGO:
• Rango Promedio: {analysis['filter_effectiveness']['avg_range_bps']:.1f} bps
• Spread Promedio: {analysis['filter_effectiveness']['avg_spread_bps']:.1f} bps
• RR ≥ 1.25: {analysis['risk_reward_analysis']['rr_above_1_25_pct']:.1f}%

🎯 CONCLUSIONES FASE 1.6:
"""
        
        # Añadir conclusiones
        conclusions = self._generate_conclusions(analysis)
        report += conclusions
        
        return report
    
    def _generate_conclusions(self, analysis: Dict[str, Any]) -> str:
        """Generar conclusiones basadas en el análisis"""
        conclusions = []
        
        # Análisis de Profit Factor
        pf = analysis['profit_factor']
        if pf >= 1.5:
            conclusions.append("✅ Profit Factor ≥ 1.5: OBJETIVO CUMPLIDO")
        elif pf >= 1.3:
            conclusions.append("⚠️ Profit Factor 1.3-1.5: CERCA DEL OBJETIVO")
        else:
            conclusions.append("❌ Profit Factor < 1.3: NECESITA MEJORAS")
        
        # Análisis de Win Rate
        wr = analysis['win_rate']
        if wr >= 60:
            conclusions.append("✅ Win Rate ≥ 60%: EXCELENTE")
        elif wr >= 50:
            conclusions.append("⚠️ Win Rate 50-60%: BUENO")
        else:
            conclusions.append("❌ Win Rate < 50%: NECESITA MEJORAS")
        
        # Análisis de TP Floor
        tp_compliance = analysis['tp_floor_compliance']['compliance_rate']
        if tp_compliance >= 95:
            conclusions.append("✅ TP Floor cumplimiento ≥ 95%: EXCELENTE")
        elif tp_compliance >= 90:
            conclusions.append("⚠️ TP Floor cumplimiento 90-95%: BUENO")
        else:
            conclusions.append("❌ TP Floor cumplimiento < 90%: PROBLEMA")
        
        # Análisis de RR
        rr_above_1_25 = analysis['risk_reward_analysis']['rr_above_1_25_pct']
        if rr_above_1_25 >= 95:
            conclusions.append("✅ RR ≥ 1.25 en ≥ 95% trades: EXCELENTE")
        elif rr_above_1_25 >= 90:
            conclusions.append("⚠️ RR ≥ 1.25 en 90-95% trades: BUENO")
        else:
            conclusions.append("❌ RR ≥ 1.25 en < 90% trades: PROBLEMA")
        
        # Análisis de fricción
        friction_impact = analysis['friction_impact']['friction_impact_pct']
        if friction_impact <= 20:
            conclusions.append("✅ Impacto fricción ≤ 20%: EXCELENTE")
        elif friction_impact <= 30:
            conclusions.append("⚠️ Impacto fricción 20-30%: ACEPTABLE")
        else:
            conclusions.append("❌ Impacto fricción > 30%: ALTO")
        
        # Recomendaciones
        recommendations = self._generate_recommendations(analysis)
        
        return "\n".join(conclusions) + "\n\n🎯 RECOMENDACIONES:\n" + recommendations
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Generar recomendaciones específicas"""
        recommendations = []
        
        # Recomendaciones basadas en Profit Factor
        pf = analysis['profit_factor']
        if pf < 1.5:
            recommendations.append("• Aumentar TP_MIN_BPS para mejorar PF")
            recommendations.append("• Revisar filtros para reducir trades perdedores")
        
        # Recomendaciones basadas en Win Rate
        wr = analysis['win_rate']
        if wr < 50:
            recommendations.append("• Mejorar filtros de entrada")
            recommendations.append("• Revisar estrategia de breakout")
        
        # Recomendaciones basadas en fricción
        friction_impact = analysis['friction_impact']['friction_impact_pct']
        if friction_impact > 30:
            recommendations.append("• Reducir frecuencia de trading")
            recommendations.append("• Optimizar para órdenes maker")
        
        # Recomendaciones generales
        recommendations.append("• Monitorear métricas por 24-48h más")
        recommendations.append("• Ajustar parámetros gradualmente")
        recommendations.append("• Considerar escalar si PF ≥ 1.5")
        
        return "\n".join(recommendations)

def main():
    """Función principal"""
    print("📊 ANALIZADOR DE DATOS GOOGLE SHEETS - FASE 1.6")
    print("=" * 60)
    
    analyzer = SheetsAnalyzer()
    
    if not analyzer.sheets_enabled:
        print("❌ No se pudo conectar a Google Sheets")
        print("💡 Asegúrate de tener credentials.json o GOOGLE_SHEETS_CREDENTIALS configurado")
        return
    
    # Generar reporte
    report = analyzer.generate_report()
    print(report)
    
    # Guardar reporte en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fase_1_6_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Reporte guardado en: {filename}")

if __name__ == "__main__":
    main()
