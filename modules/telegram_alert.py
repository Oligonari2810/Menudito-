"""
📱 NOTIFICACIONES DE TELEGRAM MEJORADAS
Sistema de alertas automáticas para el bot de trading
"""

import requests
import json
from datetime import datetime
from modules.config import TradingConfig

class TelegramAlert:
    def __init__(self):
        self.config = TradingConfig()
        self.base_url = f"https://api.telegram.org/bot{self.config.TELEGRAM['bot_token']}"
        self.chat_id = self.config.TELEGRAM['chat_id']
        
    def send_message(self, message: str) -> bool:
        """Enviar mensaje a Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error enviando mensaje por Telegram: {e}")
            return False
    
    def send_trade_alert(self, trade: dict) -> bool:
        """Enviar alerta de operación con datos completos"""
        try:
            # Calcular P&L si hay precio de salida
            pnl = 0
            pnl_text = "🔄 Operación abierta"
            if 'exit_price' in trade and trade['exit_price']:
                if trade['signal'] == 'BUY':
                    pnl = (trade['exit_price'] - trade['price']) * trade['quantity']
                else:  # SELL
                    pnl = (trade['price'] - trade['exit_price']) * trade['quantity']
                
                if pnl > 0:
                    pnl_text = f"📈 +${pnl:.2f}"
                else:
                    pnl_text = f"📉 ${pnl:.2f}"
            
            # Emoji según señal
            signal_emoji = "🟢" if trade['signal'] == 'BUY' else "🔴"
            
            # Estado de IA
            ai_status = trade.get('ai_validation', 'N/A')
            if 'CONFIRMADO' in str(ai_status):
                ai_emoji = "✅"
            elif 'RECHAZADO' in str(ai_status):
                ai_emoji = "❌"
            elif 'CAUTELA' in str(ai_status):
                ai_emoji = "⚠️"
            else:
                ai_emoji = "🤖"
            
            message = f"""
{signal_emoji} <b>ORDEN {trade['signal']} EJECUTADA</b>

💰 <b>Detalles:</b>
• Símbolo: {trade['symbol']}
• Precio: ${trade['price']:,.2f}
• Cantidad: {trade['quantity']:.6f}
• Monto: ${trade['amount']:.2f}
• Estrategia: {trade.get('strategy', 'breakout')}

📊 <b>Análisis:</b>
• Confianza: {trade.get('confidence', 0):.1f}%
• IA: {ai_emoji} {ai_status}

{pnl_text}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando alerta de trade: {e}")
            return False
    
    def send_signal_alert(self, signal: dict) -> bool:
        """Enviar alerta de señal detectada"""
        try:
            signal_emoji = "🟢" if signal['signal'] == 'BUY' else "🔴"
            
            message = f"""
{signal_emoji} <b>SEÑAL DETECTADA</b>

📊 <b>Análisis:</b>
• Señal: {signal['signal']}
• Precio: ${signal['current_price']:,.2f}
• Confianza: {signal['confidence']:.1f}%
• Estrategia: {signal.get('strategy', 'breakout')}

🧠 <b>IA:</b> {signal.get('ai_validation', 'Pendiente')}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando alerta de señal: {e}")
            return False
    
    def send_daily_report(self, stats: dict) -> bool:
        """Enviar reporte diario de rendimiento"""
        try:
            message = f"""
📊 <b>REPORTE DIARIO</b>

💰 <b>Rendimiento:</b>
• Operaciones: {stats.get('total_trades', 0)}
• Ganadas: {stats.get('winning_trades', 0)}
• Perdidas: {stats.get('losing_trades', 0)}
• P&L Total: ${stats.get('total_pnl', 0):.2f}

📈 <b>Estadísticas:</b>
• % Acierto: {stats.get('win_rate', 0):.1f}%
• Ganancia Promedio: ${stats.get('avg_win', 0):.2f}
• Pérdida Promedio: ${stats.get('avg_loss', 0):.2f}

⏰ {datetime.now().strftime('%Y-%m-%d')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando reporte diario: {e}")
            return False

    def send_startup_alert(self, config: dict = {}) -> bool:
        """Enviar alerta de inicio del bot"""
        try:
            if not config:
                config = {
                    'strategy': 'breakout',
                    'symbol': 'BTCUSDT',
                    'capital': 100,
                    'confidence_threshold': 0.4
                }
            
            message = f"""
🚀 <b>BOT DE TRADING INICIADO</b>

✅ <b>Estado:</b>
• Telegram: Conectado
• IA: {self.config.OPENAI['enabled']}
• Estrategia: {config.get('strategy', 'breakout')}
• Capital: ${config.get('capital', 100)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando alerta de inicio: {e}")
            return False
    
    def send_ai_validation_alert(self, signal: dict, ai_result: dict) -> bool:
        """Enviar alerta de validación de IA"""
        try:
            signal_emoji = "🟢" if signal['signal'] == 'BUY' else "🔴"
            
            # Estado de IA
            ai_status = ai_result.get('ai_response', 'N/A')
            if 'CONFIRMADO' in str(ai_status):
                ai_emoji = "✅"
                status_text = "CONFIRMADO"
            elif 'RECHAZADO' in str(ai_status):
                ai_emoji = "❌"
                status_text = "RECHAZADO"
            elif 'CAUTELA' in str(ai_status):
                ai_emoji = "⚠️"
                status_text = "CAUTELA"
            else:
                ai_emoji = "🤖"
                status_text = "ANÁLISIS"
            
            # Confianza ajustada
            adjusted_confidence = ai_result.get('confidence', signal.get('confidence', 0))
            
            message = f"""
{ai_emoji} <b>VALIDACIÓN DE IA</b>

{signal_emoji} <b>Señal:</b> {signal['signal']}
💰 <b>Precio:</b> ${signal.get('current_price', 0):,.2f}
🎯 <b>Confianza:</b> {signal.get('confidence', 0):.1f}% → {adjusted_confidence:.1f}%
📊 <b>Estrategia:</b> {signal.get('strategy', 'breakout')}

🧠 <b>Resultado:</b> {status_text}
📝 <b>Análisis:</b> {ai_status[:100]}...

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando alerta de validación IA: {e}")
            return False
    
    def send_error_alert(self, error: str) -> bool:
        """Enviar alerta de error"""
        try:
            message = f"""
⚠️ <b>ERROR DETECTADO</b>

❌ <b>Problema:</b>
{error}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            return self.send_message(message.strip())
            
        except Exception as e:
            print(f"Error enviando alerta de error: {e}")
            return False 