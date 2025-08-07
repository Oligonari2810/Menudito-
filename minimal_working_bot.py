#!/usr/bin/env python3
"""
🤖 Bot Mínimo Funcional
Versión simplificada que funciona sin dependencias problemáticas
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MinimalTradingBot:
    """Bot de trading mínimo funcional"""
    
    def __init__(self):
        self.is_running = True
        self.counter = 0
        self.logger = logging.getLogger(__name__)
        
        # Configuración básica
        self.symbol = "BTCUSDT"
        self.initial_capital = 50.0
        self.current_capital = 50.0
        
        # Simular datos de trading
        self.trades_history = []
        self.daily_pnl = 0.0
        
    def test_environment(self):
        """Probar variables de entorno"""
        required_vars = [
            'BINANCE_API_KEY',
            'BINANCE_SECRET_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(f"Variables faltantes: {missing_vars}")
            return False
        
        self.logger.info("✅ Variables de entorno configuradas")
        return True
    
    def send_telegram_message(self, message: str):
        """Enviar mensaje por Telegram"""
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
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    self.logger.info("✅ Mensaje enviado a Telegram")
                    return True
                else:
                    self.logger.error(f"❌ Error Telegram: {response.status_code}")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Error enviando Telegram: {e}")
            return False
    
    def simulate_trading_signal(self) -> Dict:
        """Simular señal de trading"""
        import random
        
        signals = ["BUY", "SELL", "WAIT"]
        signal = random.choice(signals)
        
        if signal == "WAIT":
            return {
                'signal': 'WAIT',
                'reason': 'Sin señales claras',
                'confidence': 0.0
            }
        
        # Simular precio de BTC
        btc_price = 115000 + random.uniform(-5000, 5000)
        
        return {
            'signal': signal,
            'reason': f'Señal simulada - {signal} BTC',
            'confidence': random.uniform(0.1, 0.8),
            'price': btc_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_trade(self, signal: Dict) -> Dict:
        """Simular operación de trading"""
        if signal['signal'] == 'WAIT':
            return None
        
        # Simular resultado
        import random
        success = random.choice([True, False])
        
        if success:
            profit = random.uniform(0.5, 2.0)
            self.current_capital += profit
            self.daily_pnl += profit
            result = "GANANCIA"
        else:
            loss = random.uniform(0.3, 1.5)
            self.current_capital -= loss
            self.daily_pnl -= loss
            result = "PÉRDIDA"
        
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'side': signal['signal'],
            'price': signal['price'],
            'amount': 10.0,
            'result': result,
            'pnl': profit if success else -loss,
            'capital': self.current_capital
        }
        
        self.trades_history.append(trade)
        return trade
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading"""
        try:
            self.counter += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.logger.info(f"🔄 Ciclo {self.counter} - {current_time}")
            
            # Generar señal
            signal = self.simulate_trading_signal()
            self.logger.info(f"📊 Señal: {signal['signal']} - {signal['reason']}")
            
            # Ejecutar operación si hay señal
            if signal['signal'] != 'WAIT':
                trade = self.simulate_trade(signal)
                if trade:
                    self.logger.info(f"💰 Trade: {trade['side']} {self.symbol} @ ${trade['price']:,.2f} - {trade['result']}")
                    
                    # Enviar alerta a Telegram
                    alert_msg = f"🤖 BOT MÍNIMO\n\n💰 Trade: {trade['side']} {self.symbol}\n💵 Precio: ${trade['price']:,.2f}\n📊 Resultado: {trade['result']}\n💸 P&L: ${trade['pnl']:.2f}\n🏦 Capital: ${self.current_capital:.2f}"
                    self.send_telegram_message(alert_msg)
            else:
                self.logger.info("⏳ Esperando señales...")
            
            # Enviar reporte cada 10 ciclos
            if self.counter % 10 == 0:
                report_msg = f"📊 REPORTE BOT MÍNIMO\n\n🔄 Ciclos: {self.counter}\n💰 Capital: ${self.current_capital:.2f}\n📈 P&L Diario: ${self.daily_pnl:.2f}\n📊 Operaciones: {len(self.trades_history)}"
                self.send_telegram_message(report_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo: {e}")
    
    def start(self):
        """Iniciar bot"""
        self.logger.info("🚀 Iniciando bot mínimo funcional...")
        
        # Probar entorno
        if not self.test_environment():
            self.logger.warning("⚠️ Algunas variables faltan, continuando...")
        
        # Enviar mensaje de inicio
        start_msg = "🤖 BOT MÍNIMO INICIADO\n\n✅ Funcionando sin dependencias problemáticas\n📊 Modo simulación activado\n🔄 Ciclos cada 60 segundos\n📱 Alertas Telegram habilitadas"
        self.send_telegram_message(start_msg)
        
        self.logger.info("✅ Bot mínimo iniciado correctamente")
        
        # Bucle principal
        while self.is_running:
            try:
                self.run_trading_cycle()
                time.sleep(60)  # Esperar 1 minuto
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Bot detenido por usuario")
                break
            except Exception as e:
                self.logger.error(f"❌ Error en bucle principal: {e}")
                time.sleep(30)

def main():
    """Función principal"""
    print("🤖 BOT MÍNIMO FUNCIONAL")
    print("=" * 50)
    
    try:
        bot = MinimalTradingBot()
        bot.start()
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
