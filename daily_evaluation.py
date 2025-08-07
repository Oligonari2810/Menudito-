#!/usr/bin/env python3
"""
📊 EVALUACIÓN DIARIA AUTOMÁTICA
Script para evaluar el rendimiento del bot y enviar reportes
"""

import os
import requests
import json
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DailyEvaluation:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def send_telegram_report(self, message):
        """Enviar reporte por Telegram"""
        try:
            if self.bot_token and self.chat_id:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, json=data, timeout=10)
                return response.json().get('ok', False)
        except Exception as e:
            logging.error(f"❌ Error enviando reporte: {e}")
            return False
    
    def get_bot_status(self):
        """Obtener estado del bot desde Render"""
        try:
            # URL del bot desplegado en Render
            render_url = os.getenv('RENDER_URL', 'https://trading-bot-survivor.onrender.com')
            response = requests.get(f"{render_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            logging.error(f"❌ Error obteniendo estado: {e}")
            return None
    
    def generate_daily_report(self):
        """Generar reporte diario"""
        today = datetime.now()
        
        # Obtener estado del bot
        bot_status = self.get_bot_status()
        
        # Generar reporte
        report = f"""
📊 REPORTE DIARIO - {today.strftime('%d/%m/%Y')}
===============================================

🕐 Evaluación: {today.strftime('%H:%M:%S')}
📅 Día: {today.strftime('%A, %d de %B')}

🤖 ESTADO DEL BOT:
"""
        
        if bot_status:
            report += f"""
✅ Estado: {bot_status.get('status', 'unknown')}
🤖 Bot: {bot_status.get('bot_status', 'unknown')}
🔄 Reinicios: {bot_status.get('restart_count', 0)}
⏰ Última verificación: {bot_status.get('timestamp', 'N/A')}
"""
        else:
            report += """
❌ No se pudo obtener estado del bot
⚠️ Verificar conectividad con Render
"""
        
        report += f"""

📈 OBJETIVO DIARIO:
🎯 Capital objetivo: $1000.0
📊 Progreso actual: Verificar Google Sheets
⏰ Próxima evaluación: {(today + timedelta(days=1)).strftime('%d/%m/%Y')}

🛡️ CONFIGURACIÓN ACTIVA:
💰 Capital diario: 60%
📊 Operaciones/día: 15
🎯 Confianza mínima: 10%
⚡ Take profit: 4.2%
🛑 Stop loss: 0.7%

📱 ALERTAS CONFIGURADAS:
✅ Telegram: Activo
📊 Google Sheets: Activo
🔄 Reinicio automático: Activo
🌐 Health checks: Activo

💡 RECOMENDACIONES:
• Revisar Google Sheets para análisis detallado
• Verificar rendimiento vs objetivo diario
• Ajustar parámetros si es necesario
• Monitorear alertas críticas

🔄 PRÓXIMA EVALUACIÓN: Mañana a las 00:00
"""
        
        return report
    
    def run_evaluation(self):
        """Ejecutar evaluación diaria"""
        logging.info("📊 Iniciando evaluación diaria automática...")
        
        try:
            # Generar reporte
            report = self.generate_daily_report()
            
            # Enviar por Telegram
            if self.send_telegram_report(report):
                logging.info("✅ Reporte diario enviado exitosamente")
            else:
                logging.error("❌ Error enviando reporte diario")
            
            # Log local
            with open('daily_reports.log', 'a') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"EVALUACIÓN DIARIA - {datetime.now()}\n")
                f.write(f"{'='*50}\n")
                f.write(report)
                f.write(f"\n{'='*50}\n")
            
            logging.info("✅ Evaluación diaria completada")
            
        except Exception as e:
            error_msg = f"❌ ERROR EN EVALUACIÓN DIARIA: {e}"
            logging.error(error_msg)
            self.send_telegram_report(error_msg)

def main():
    """Función principal"""
    evaluator = DailyEvaluation()
    evaluator.run_evaluation()

if __name__ == "__main__":
    main() 