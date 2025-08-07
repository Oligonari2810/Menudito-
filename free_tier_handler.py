#!/usr/bin/env python3
"""
🆓 Manejador para Plan Gratuito de Render
Script para manejar las limitaciones del plan gratuito
"""

import os
import time
import logging
import requests
from datetime import datetime

class FreeTierHandler:
    def __init__(self):
        self.is_free_tier = os.getenv('RENDER_FREE_TIER', 'false').lower() == 'true'
        self.health_check_url = os.getenv('RENDER_HEALTH_CHECK_URL', '')
        
    def setup_free_tier_config(self):
        """Configurar para plan gratuito"""
        if not self.is_free_tier:
            return
            
        logging.info("🆓 Configurando para plan gratuito de Render...")
        
        # Configuraciones específicas para plan gratuito
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        
        # Timeouts más largos para APIs
        os.environ['BINANCE_TIMEOUT'] = '30'
        os.environ['TELEGRAM_TIMEOUT'] = '30'
        os.environ['OPENAI_TIMEOUT'] = '60'
        
        logging.info("✅ Configuración para plan gratuito aplicada")
    
    def keep_alive(self):
        """Mantener el servicio activo"""
        if not self.is_free_tier:
            return
            
        try:
            # Ping al health check para mantener activo
            if self.health_check_url:
                requests.get(self.health_check_url, timeout=5)
                logging.info("🔄 Ping enviado para mantener servicio activo")
        except Exception as e:
            logging.warning(f"⚠️ Error en ping: {e}")
    
    def handle_sleep_wake_cycle(self):
        """Manejar ciclo de sleep/wake"""
        if not self.is_free_tier:
            return
            
        logging.info("⏰ Detectado plan gratuito - manejando sleep/wake cycle")
        
        # Enviar ping cada 10 minutos para mantener activo
        while True:
            try:
                self.keep_alive()
                time.sleep(600)  # 10 minutos
            except Exception as e:
                logging.error(f"❌ Error en keep alive: {e}")
                time.sleep(60)
    
    def optimize_for_free_tier(self):
        """Optimizar para plan gratuito"""
        if not self.is_free_tier:
            return
            
        logging.info("🆓 Optimizando para plan gratuito...")
        
        # Reducir frecuencia de operaciones
        os.environ['TRADING_INTERVAL'] = '120'  # 2 minutos en lugar de 1
        
        # Reducir logging para ahorrar recursos
        logging.getLogger().setLevel(logging.WARNING)
        
        # Configurar timeouts más largos
        os.environ['REQUEST_TIMEOUT'] = '30'
        
        logging.info("✅ Optimización para plan gratuito aplicada")

def main():
    """Función principal"""
    handler = FreeTierHandler()
    
    if handler.is_free_tier:
        print("🆓 Detectado plan gratuito de Render")
        handler.setup_free_tier_config()
        handler.optimize_for_free_tier()
        
        # Iniciar keep alive en hilo separado
        import threading
        keep_alive_thread = threading.Thread(
            target=handler.handle_sleep_wake_cycle,
            daemon=True
        )
        keep_alive_thread.start()
        
        print("✅ Configuración para plan gratuito aplicada")
    else:
        print("💎 Plan pagado detectado - sin limitaciones")

if __name__ == "__main__":
    main()
