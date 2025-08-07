"""
🧠 VALIDACIÓN CON IA - OpenAI GPT-4
Sistema de validación inteligente para operaciones de trading
"""

import logging
from typing import Dict, Optional
from modules.config import TradingConfig

class AIValidator:
    """Validación de operaciones con OpenAI GPT-4"""
    
    def __init__(self):
        """Inicializar validador de IA"""
        self.config = TradingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Verificar configuración de OpenAI
        if not self.config.OPENAI['enabled']:
            self.logger.warning("OpenAI no configurado - validación de IA deshabilitada")
            return
        
        try:
            # Verificar que OpenAI esté configurado
            if not hasattr(self.config, 'OPENAI') or not self.config.OPENAI.get('enabled'):
                self.logger.warning("OpenAI no configurado - validación de IA deshabilitada")
                return
            
            self.logger.info("✅ OpenAI configurado correctamente")
        except Exception as e:
            self.logger.error(f"Error configurando OpenAI: {e}")
    
    def validate_signal(self, signal: Dict, market_data: Dict) -> Dict:
        """
        Validar señal de trading con IA
        
        Args:
            signal: Señal de trading
            market_data: Datos del mercado
            
        Returns:
            Resultado de validación
        """
        if not hasattr(self.config, 'OPENAI') or not self.config.OPENAI.get('enabled'):
            return {
                'validated': True,
                'confidence': signal.get('confidence', 0.3),
                'reason': 'IA no configurada - validación automática',
                'ai_response': 'SIN VALIDACIÓN DE IA'
            }
        
        try:
            # Crear prompt para GPT-4
            prompt = self._create_validation_prompt(signal, market_data)
            
            # Consultar OpenAI (nueva versión)
            from openai import OpenAI
            client = OpenAI(api_key=self.config.OPENAI['api_key'])
            
            # Agregar timeout para evitar bloqueos
            import signal as signal_module
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout en consulta de IA")
            
            # Configurar timeout de 10 segundos
            signal_module.signal(signal_module.SIGALRM, timeout_handler)
            signal_module.alarm(10)
            
            try:
                response = client.chat.completions.create(
                    model=self.config.OPENAI['model'],
                    messages=[
                        {
                            "role": "system",
                            "content": """Eres un experto analista de trading que valida señales de trading. 
                            Responde solo con: CONFIRMADO, RECHAZADO, o CAUTELA. 
                            Luego explica brevemente tu decisión en una línea."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.config.OPENAI['max_tokens'],
                    temperature=self.config.OPENAI['temperature']
                )
                
                signal_module.alarm(0)  # Cancelar timeout
                if response.choices and response.choices[0].message and response.choices[0].message.content:
                    ai_response = response.choices[0].message.content.strip()
                else:
                    ai_response = "CAUTELA - Respuesta vacía de IA"
                
            except TimeoutError:
                signal_module.alarm(0)  # Cancelar timeout
                self.logger.warning("⚠️ Timeout en consulta de IA, usando fallback")
                ai_response = "CAUTELA - Timeout en consulta de IA"
            except Exception as e:
                signal_module.alarm(0)  # Cancelar timeout
                self.logger.error(f"Error en consulta de IA: {e}")
                ai_response = "CAUTELA - Error en consulta de IA"
            
            # Procesar respuesta
            if "CONFIRMADO" in ai_response.upper():
                validated = True
                confidence_boost = 0.1  # +10% de confianza
            elif "RECHAZADO" in ai_response.upper():
                validated = False
                confidence_boost = -0.2  # -20% de confianza
            else:  # CAUTELA
                # NUEVA LÓGICA: Para testnet, aceptar CAUTELA si confianza ≥ 15%
                signal_confidence = signal.get('confidence', 0.3)
                if signal_confidence >= 0.15:
                    validated = True
                    self.logger.info(f"✅ Aceptando señal con CAUTELA (confianza: {signal_confidence:.1%})")
                else:
                    validated = False
                    self.logger.info(f"❌ Rechazando señal con CAUTELA (confianza baja: {signal_confidence:.1%})")
                confidence_boost = 0.0  # Sin cambio
            
            # Ajustar confianza
            signal_confidence = signal.get('confidence', 0.3)
            adjusted_confidence = min(0.95, signal_confidence + confidence_boost)
            
            return {
                'validated': validated,
                'confidence': adjusted_confidence,
                'reason': ai_response,
                'ai_response': ai_response,
                'confidence_boost': confidence_boost
            }
            
        except Exception as e:
            self.logger.error(f"Error en validación de IA: {e}")
            return {
                'validated': True,
                'confidence': signal.get('confidence', 0.3),
                'reason': f'Error de IA: {str(e)}',
                'ai_response': 'CAUTELA - Error de IA',
                'confidence_boost': 0.0
            }
    
    def _create_validation_prompt(self, signal: Dict, market_data: Dict) -> str:
        """
        Crear prompt para validación de IA
        
        Args:
            signal: Señal de trading
            market_data: Datos del mercado
            
        Returns:
            Prompt para GPT-4
        """
        current_price = signal['current_price']
        strategy = signal['strategy']
        confidence = signal['confidence']
        
        # Información del mercado
        market_info = f"""
Precio actual: ${current_price:,.2f}
Estrategia: {strategy.upper()}
Confianza del sistema: {confidence:.1%}
"""
        
        # Información específica según estrategia
        if strategy == 'breakout':
            support = signal.get('support', 0)
            resistance = signal.get('resistance', 0)
            volume_ratio = signal.get('volume_ratio', 1.0)
            
            strategy_info = f"""
Análisis de Breakout:
- Soporte: ${support:,.2f}
- Resistencia: ${resistance:,.2f}
- Ratio de volumen: {volume_ratio:.2f}
- Señal: {signal['signal']} - {signal['reason']}
"""
        elif strategy == 'scalping':
            avg_change = signal.get('avg_change', 0)
            volatility = signal.get('volatility', 0)
            momentum = signal.get('momentum', 0)
            
            strategy_info = f"""
Análisis de Scalping:
- Cambio promedio: {avg_change:.2f}%
- Volatilidad: {volatility:.2f}%
- Momentum: {momentum:.2f}%
- Señal: {signal['signal']} - {signal['reason']}
"""
        else:
            strategy_info = f"Señal: {signal['signal']} - {signal['reason']}"
        
        # Crear prompt completo
        prompt = f"""
Validar esta señal de trading:

{market_info}
{strategy_info}

Considera:
1. ¿La señal es técnicamente sólida?
2. ¿El volumen confirma el movimiento?
3. ¿La tendencia general es favorable?
4. ¿El riesgo/recompensa es aceptable?

Responde: CONFIRMADO, RECHAZADO, o CAUTELA + explicación breve.
"""
        
        return prompt
    
    def analyze_market_sentiment(self, market_data: Dict) -> Dict:
        """
        Analizar sentimiento del mercado con IA
        
        Args:
            market_data: Datos del mercado
            
        Returns:
            Análisis de sentimiento
        """
        if not self.config.OPENAI['enabled']:
            return {'sentiment': 'neutral', 'reason': 'IA no configurada'}
        
        try:
            prompt = f"""
Analiza el sentimiento del mercado para BTC:

Precio actual: ${market_data.get('current_price', 0):,.2f}
Volumen 24h: {market_data.get('volume_24h', 0):,.0f}
Cambio 24h: {market_data.get('change_24h', 0):.2f}%

Responde solo: BULLISH, BEARISH, o NEUTRAL + razón breve.
"""
            
            from openai import OpenAI
            client = OpenAI(api_key=self.config.OPENAI['api_key'])
            
            response = client.chat.completions.create(
                model=self.config.OPENAI['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista de sentimiento de mercado. Responde solo: BULLISH, BEARISH, o NEUTRAL + explicación."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )

            # Validamos que la respuesta de la IA exista y sea una cadena antes de aplicar strip()
            try:
                ai_response = response.choices[0].message.content
                if isinstance(ai_response, str):
                    ai_response = ai_response.strip()
                else:
                    ai_response = ""
            except Exception as e:
                self.logger.error(f"Error al obtener el contenido de la respuesta de la IA: {e}")
                ai_response = ""

            if "BULLISH" in ai_response.upper():
                sentiment = "bullish"
            elif "BEARISH" in ai_response.upper():
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            return {
                'sentiment': sentiment,
                'reason': ai_response
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando sentimiento: {e}")
            return {'sentiment': 'neutral', 'reason': f'Error: {str(e)}'}
    
    def get_risk_assessment(self, signal: Dict) -> Dict:
        """
        Evaluar riesgo de la operación con IA
        
        Args:
            signal: Señal de trading
            
        Returns:
            Evaluación de riesgo
        """
        if not self.config.OPENAI['enabled']:
            return {'risk_level': 'medium', 'reason': 'IA no configurada'}
        
        try:
            prompt = f"""
Evalúa el riesgo de esta operación:

Señal: {signal['signal']}
Estrategia: {signal['strategy']}
Confianza: {signal['confidence']:.1%}
Precio: ${signal['current_price']:,.2f}

Responde solo: BAJO, MEDIO, o ALTO + razón breve.
"""
            
            from openai import OpenAI
            client = OpenAI(api_key=self.config.OPENAI['api_key'])
            
            response = client.chat.completions.create(
                model=self.config.OPENAI['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista de riesgo. Responde solo: BAJO, MEDIO, o ALTO + explicación."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )

            contenido_mensaje = response.choices[0].message.content if response.choices[0].message and response.choices[0].message.content else ""
            ai_response = contenido_mensaje.strip()
            
            if "BAJO" in ai_response.upper():
                risk_level = "low"
            elif "ALTO" in ai_response.upper():
                risk_level = "high"
            else:
                risk_level = "medium"
            
            return {
                'risk_level': risk_level,
                'reason': ai_response
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando riesgo: {e}")
            return {'risk_level': 'medium', 'reason': f'Error: {str(e)}'} 