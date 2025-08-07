#!/usr/bin/env python3
"""
🚀 DEPLOY PROFESIONAL PARA RENDER
Script optimizado para ejecutar el bot profesional en Render
"""

import os
import time
import signal
import logging
import subprocess
from flask import Flask, request, jsonify

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar Flask
app = Flask(__name__)

# Variables globales
bot_process = None
is_shutting_down = False

def handle_shutdown(signum, frame):
    """Manejar cierre graceful"""
    global is_shutting_down, bot_process
    logger.info("🛑 Señal de terminación recibida en deploy")
    is_shutting_down = True
    
    if bot_process:
        logger.info("🔄 Terminando proceso del bot...")
        try:
            bot_process.terminate()
            bot_process.wait(timeout=10)
            logger.info("✅ Proceso del bot terminado")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Forzando terminación del bot...")
            bot_process.kill()
        except Exception as e:
            logger.error(f"❌ Error terminando bot: {e}")

def start_bot():
    """Iniciar el bot profesional"""
    global bot_process
    
    try:
        logger.info("🚀 Iniciando bot profesional...")
        
        # Comando para ejecutar el bot
        cmd = ["python3", "minimal_working_bot.py"]
        
        # Iniciar proceso del bot
        bot_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"✅ Bot iniciado con PID: {bot_process.pid}")
        
        # Monitorear salida del bot
        while bot_process.poll() is None and not is_shutting_down:
            try:
                output = bot_process.stdout.readline()
                if output:
                    logger.info(f"🤖 BOT: {output.strip()}")
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"❌ Error leyendo salida del bot: {e}")
                break
        
        # Verificar estado final
        if bot_process.returncode is not None:
            logger.info(f"📊 Bot terminado con código: {bot_process.returncode}")
        else:
            logger.info("✅ Bot ejecutándose correctamente")
            
    except Exception as e:
        logger.error(f"❌ Error iniciando bot: {e}")
        raise

@app.route('/')
def health_check():
    """Health check para Render"""
    global bot_process
    
    if bot_process and bot_process.poll() is None:
        return jsonify({
            'status': 'healthy',
            'bot_running': True,
            'pid': bot_process.pid,
            'timestamp': time.time()
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'bot_running': False,
            'timestamp': time.time()
        }), 503

@app.route('/health')
def health():
    """Endpoint de health check"""
    return health_check()

@app.route('/status')
def status():
    """Endpoint de status detallado"""
    global bot_process
    
    status_info = {
        'service': 'Trading Bot Professional',
        'version': '1.0.0',
        'timestamp': time.time(),
        'bot_running': bot_process and bot_process.poll() is None,
        'pid': bot_process.pid if bot_process else None,
        'return_code': bot_process.returncode if bot_process else None
    }
    
    return jsonify(status_info), 200

def main():
    """Función principal"""
    global bot_process
    
    # Configurar manejo de señales
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    logger.info("🚀 DEPLOY PROFESIONAL INICIADO")
    logger.info("=" * 50)
    
    try:
        # Iniciar bot en background
        import threading
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
        logger.info("✅ Bot iniciado en background")
        logger.info("🌐 Iniciando servidor web en puerto 10000")
        
        # Iniciar Flask
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 10000)),
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Deploy detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error en deploy: {e}")
        raise
    finally:
        # Limpiar proceso del bot
        if bot_process:
            try:
                bot_process.terminate()
                bot_process.wait(timeout=5)
            except:
                pass

if __name__ == "__main__":
    main() 