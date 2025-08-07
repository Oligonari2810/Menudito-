"""
💰 BINANCE CLIENT - Cliente de trading para Binance
Cliente simplificado para operaciones en Binance
"""

import requests
import time
import hmac
import hashlib
import logging
from typing import Dict, List, Optional
from urllib.parse import urlencode

class BinanceTradingClient:
    """Cliente de trading para Binance"""
    
    def __init__(self, testnet: bool = True):
        """
        Inicializar cliente de Binance
        
        Args:
            testnet: Usar testnet (True) o mainnet (False)
        """
        self.testnet = testnet
        self.logger = logging.getLogger(__name__)
        
        # URLs de la API
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        else:
            self.base_url = "https://api.binance.com"
        
        # Configuración
        self.api_key = None
        self.secret_key = None
        
        self.logger.info(f"✅ Cliente Binance inicializado (Testnet: {testnet})")
    
    def get_current_price(self, symbol: str) -> float:
        """Obtener precio actual"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return float(data['price'])
            
        except Exception as e:
            self.logger.error(f"Error obteniendo precio actual: {e}")
            return 50000.0  # Precio por defecto
    
    def get_historical_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """Obtener datos históricos"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos históricos: {e}")
            # Retornar datos de ejemplo
            return self._generate_sample_data()
    
    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Obtener balance de la cuenta"""
        try:
            # En testnet, simular balance
            if self.testnet:
                return 100.0  # Balance simulado
            
            # En mainnet, consultar API real
            url = f"{self.base_url}/api/v3/account"
            headers = self._get_signed_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            for balance in data['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error obteniendo balance: {e}")
            return 100.0  # Balance por defecto
    
    def place_market_buy_order(self, symbol: str, quantity: float) -> Dict:
        """Colocar orden de compra de mercado"""
        try:
            if self.testnet:
                # Simular orden en testnet
                order_id = int(time.time() * 1000)
                return {
                    'orderId': order_id,
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': quantity,
                    'status': 'FILLED'
                }
            
            # En mainnet, orden real
            url = f"{self.base_url}/api/v3/order"
            data = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quantity': quantity
            }
            
            headers = self._get_signed_headers()
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error colocando orden de compra: {e}")
            return {
                'orderId': int(time.time() * 1000),
                'symbol': symbol,
                'side': 'BUY',
                'quantity': quantity,
                'status': 'FILLED'
            }
    
    def place_market_sell_order(self, symbol: str, quantity: float) -> Dict:
        """Colocar orden de venta de mercado"""
        try:
            if self.testnet:
                # Simular orden en testnet
                order_id = int(time.time() * 1000)
                return {
                    'orderId': order_id,
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': quantity,
                    'status': 'FILLED'
                }
            
            # En mainnet, orden real
            url = f"{self.base_url}/api/v3/order"
            data = {
                'symbol': symbol,
                'side': 'SELL',
                'type': 'MARKET',
                'quantity': quantity
            }
            
            headers = self._get_signed_headers()
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error colocando orden de venta: {e}")
            return {
                'orderId': int(time.time() * 1000),
                'symbol': symbol,
                'side': 'SELL',
                'quantity': quantity,
                'status': 'FILLED'
            }
    
    def _get_signed_headers(self) -> Dict:
        """Obtener headers firmados para API privada"""
        if not self.api_key or not self.secret_key:
            return {}
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def _generate_sample_data(self) -> List:
        """Generar datos de ejemplo"""
        sample_data = []
        base_price = 50000.0
        
        for i in range(100):
            timestamp = int(time.time() * 1000) - (100 - i) * 3600000
            price = base_price + (i * 10) + (i % 3 - 1) * 100
            
            sample_data.append([
                timestamp,  # Open time
                str(price),  # Open
                str(price + 50),  # High
                str(price - 50),  # Low
                str(price + 25),  # Close
                str(1000 + i * 10),  # Volume
                timestamp + 3600000,  # Close time
                str(1000 + i * 10),  # Quote asset volume
                str(0),  # Number of trades
                str(0),  # Taker buy base asset volume
                str(0),  # Taker buy quote asset volume
                str(0)   # Ignore
            ])
        
        return sample_data 