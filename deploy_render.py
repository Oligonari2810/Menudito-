#!/usr/bin/env python3
"""
🚀 DESPLIEGUE AUTÓNOMO EN RENDER
Script para ejecutar el bot de trading de forma continua en Render
"""

import os
import subprocess
import time
import logging
import threading
from datetime import datetime
import requests
from flask import Flask, jsonify
import signal
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('render_deployment.log'),
        logging.StreamHandler()
    ]
)

# Crear aplicación Flask para health checks
app = Flask(__name__)

class RenderDeployment:
    def __init__(self):
        self.bot_process = None
        self.restart_count = 0
        self.max_restarts = 50  # Más reinicios para Render
        self.is_running = True
        
    def start_bot(self):
        """Iniciar el bot de trading"""
        try:
            logging.info("🚀 Iniciando bot de trading en Render...")
            
            # Primero ejecutar pruebas
            logging.info("🧪 Ejecutando pruebas de verificación...")
            test_result = subprocess.run(
                ["python3", "test_bot_startup.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if test_result.returncode != 0:
                logging.error("❌ Pruebas fallaron, no se puede iniciar el bot")
                logging.error(f"📤 STDOUT: {test_result.stdout}")
                logging.error(f"📤 STDERR: {test_result.stderr}")
                return False
            
            logging.info("✅ Pruebas pasaron, iniciando bot...")
            
            # Comando para ejecutar el bot
            cmd = [
                "python3", "main_survivor.py",
                "--strategy", "breakout"
            ]
            
            logging.info(f"📋 Comando: {' '.join(cmd)}")
            
            self.bot_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logging.info(f"✅ Bot iniciado con PID: {self.bot_process.pid}")
            
            # Esperar un momento para ver si el bot se inicia correctamente
            time.sleep(5)
            
            # Verificar si el proceso sigue ejecutándose
            if self.bot_process.poll() is None:
                logging.info("✅ Bot iniciado correctamente")
                return True
            else:
                # Capturar la salida de error
                stdout, stderr = self.bot_process.communicate()
                logging.error(f"❌ Bot se cerró inmediatamente")
                logging.error(f"📤 STDOUT: {stdout}")
                logging.error(f"📤 STDERR: {stderr}")
                return False
            
        except Exception as e:
            logging.error(f"❌ Error iniciando bot: {e}")
            return False
    
    def check_bot_health(self):
        """Verificar salud del bot"""
        if self.bot_process is None:
            return False
            
        # Verificar si el proceso sigue ejecutándose
        if self.bot_process.poll() is None:
            return True
        else:
            logging.warning("⚠️ Bot se detuvo inesperadamente")
            return False
    
    def restart_bot(self):
        """Reiniciar el bot"""
        if self.restart_count >= self.max_restarts:
            logging.error("🛑 Máximo número de reinicios alcanzado")
            return False
            
        logging.info(f"🔄 Reiniciando bot (intento {self.restart_count + 1}/{self.max_restarts})")
        
        if self.bot_process:
            self.bot_process.terminate()
            time.sleep(5)
            
        self.restart_count += 1
        return self.start_bot()
    
    def send_telegram_alert(self, message):
        """Enviar alerta por Telegram"""
        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if bot_token and chat_id:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                requests.post(url, json=data, timeout=10)
                
        except Exception as e:
            logging.error(f"❌ Error enviando alerta Telegram: {e}")
    
    def monitor_bot(self):
        """Monitorear el bot en un hilo separado"""
        logging.info("🛡️ Iniciando monitoreo autónomo del bot...")
        
        # Enviar alerta de inicio
        self.send_telegram_alert(
            "☁️ BOT DESPLEGADO EN RENDER\n\n"
            "🚀 Ejecutándose de forma autónoma\n"
            "📊 Monitoreo 24/7 activado\n"
            "🛡️ Reinicio automático configurado\n"
            "📱 Alertas críticas habilitadas\n"
            "🌐 Health checks activos"
        )
        
        while self.is_running:
            try:
                # Verificar salud del bot
                if not self.check_bot_health():
                    logging.warning("⚠️ Bot no responde, reiniciando...")
                    
                    if not self.restart_bot():
                        error_msg = "🛑 ERROR CRÍTICO: No se pudo reiniciar el bot"
                        logging.error(error_msg)
                        self.send_telegram_alert(error_msg)
                        break
                    else:
                        self.send_telegram_alert(
                            "🔄 BOT REINICIADO AUTOMÁTICAMENTE\n\n"
                            f"📊 Intento: {self.restart_count}\n"
                            "✅ Operación restaurada\n"
                            "🛡️ Monitoreo continuo activo"
                        )
                
                # Esperar antes de la siguiente verificación
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logging.error(f"❌ Error en monitoreo: {e}")
                time.sleep(30)
    
    def cleanup(self):
        """Limpiar recursos al salir"""
        self.is_running = False
        if self.bot_process:
            self.bot_process.terminate()
            logging.info("✅ Proceso del bot terminado")

# Instancia global del deployment
deployment = RenderDeployment()

# Rutas Flask para health checks
@app.route('/health')
def health_check():
    """Health check para Render"""
    bot_status = "running" if deployment.check_bot_health() else "stopped"
    return jsonify({
        "status": "healthy",
        "bot_status": bot_status,
        "restart_count": deployment.restart_count,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/')
def home():
    """Página principal"""
    return jsonify({
        "message": "Trading Bot Survivor - Desplegado en Render",
        "status": "operational",
        "bot_pid": deployment.bot_process.pid if deployment.bot_process else None
    })

@app.route('/restart')
def restart_bot():
    """Endpoint para reiniciar el bot manualmente"""
    if deployment.restart_bot():
        return jsonify({"status": "success", "message": "Bot reiniciado"})
    else:
        return jsonify({"status": "error", "message": "No se pudo reiniciar el bot"})

def signal_handler(signum, frame):
    """Manejador de señales para limpieza"""
    logging.info("🛑 Señal de terminación recibida")
    deployment.cleanup()
    sys.exit(0)

def main():
    """Función principal"""
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar bot
    if deployment.start_bot():
        # Iniciar monitoreo en hilo separado
        monitor_thread = threading.Thread(target=deployment.monitor_bot, daemon=True)
        monitor_thread.start()
        
        # Iniciar servidor Flask
        port = int(os.environ.get('PORT', 10000))
        logging.info(f"🌐 Iniciando servidor web en puerto {port}")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
    else:
        logging.error("❌ No se pudo iniciar el bot")

if __name__ == "__main__":
    main() 