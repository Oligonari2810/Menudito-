#!/usr/bin/env python3
"""
📊 SHEETS LOGGER - Registro de operaciones en Google Sheets
Conecta con Google Sheets y registra todas las operaciones del bot
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import csv
from typing import Dict, Optional

class SheetsLogger:
    """Logger para Google Sheets"""
    
    def __init__(self, spreadsheet_name: str = "Trading Bot Log"):
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.credentials_file = 'credentials.json'
        
        # Configurar credenciales
        self.setup_credentials()
        
    def setup_credentials(self) -> bool:
        """Configurar credenciales de Google Sheets"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"❌ Archivo {self.credentials_file} no encontrado")
                return False
            
            # Configurar scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Cargar credenciales
            # Corregido para cumplir con los tipos esperados por gspread y oauth2client
            # Usar google-auth en lugar de oauth2client, ya que oauth2client está obsoleto
            from google.oauth2.service_account import Credentials as GoogleCredentials

            credentials = GoogleCredentials.from_service_account_file(
                self.credentials_file,
                scopes=scope
            )
            # Solución: usar google-auth en lugar de oauth2client
            from google.oauth2.service_account import Credentials as GoogleCredentials

            credentials = GoogleCredentials.from_service_account_file(
                self.credentials_file,
                scopes=scope
            )
            self.client = gspread.authorize(credentials)
            print("✅ Credenciales de Google Sheets configuradas")
            return True

        except Exception as e:
            print(f"❌ Error configurando credenciales: {e}")
            return False
    
    def open_or_create_spreadsheet(self) -> bool:
        """Abrir o crear spreadsheet"""
        try:
            if not self.client:
                print("❌ Cliente no inicializado")
                return False
            
            # Intentar abrir spreadsheet existente
            try:
                self.spreadsheet = self.client.open(self.spreadsheet_name)
                print(f"✅ Spreadsheet '{self.spreadsheet_name}' abierto")
            except gspread.SpreadsheetNotFound:
                try:
                    # Crear nuevo spreadsheet
                    self.spreadsheet = self.client.create(self.spreadsheet_name)
                    # Hacer público para acceso
                    self.spreadsheet.share('', perm_type='anyone', role='reader')
                    print(f"✅ Spreadsheet '{self.spreadsheet_name}' creado")
                except Exception as e:
                    if "quota" in str(e).lower():
                        print("⚠️ Cuota de Google Drive excedida")
                        print("💡 Solución: Usar spreadsheet existente")
                        # Intentar usar un spreadsheet existente
                        try:
                            # Listar spreadsheets disponibles
                            spreadsheets = self.client.openall()
                            if spreadsheets:
                                self.spreadsheet = spreadsheets[0]
                                print(f"✅ Usando spreadsheet existente: {self.spreadsheet.title}")
                            else:
                                print("❌ No hay spreadsheets disponibles")
                                return False
                        except Exception as e2:
                            print(f"❌ Error accediendo a spreadsheets: {e2}")
                            return False
            
            # Obtener o crear worksheet
            try:
                if self.spreadsheet:
                    self.worksheet = self.spreadsheet.worksheet("Trading Log")
                    print("✅ Worksheet 'Trading Log' encontrado")
                else:
                    print("❌ Spreadsheet no inicializado")
                    return False
            except gspread.WorksheetNotFound:
                try:
                    if self.spreadsheet:
                        self.worksheet = self.spreadsheet.add_worksheet("Trading Log", 1000, 20)
                    else:
                        print("❌ Spreadsheet no inicializado")
                        return False
                    # Crear headers
                    headers = [
                        'Fecha', 'Hora', 'Símbolo', 'Dirección', 'Precio Entrada',
                        'Cantidad', 'Monto', 'Estrategia', 'Confianza', 
                        'IA Validación', 'Resultado', 'P&L', 'Balance'
                    ]
                    if self.worksheet:
                        self.worksheet.append_row(headers)
                        print("✅ Headers creados en worksheet")
                    else:
                        print("❌ Worksheet no inicializado")
                        return False
                except Exception as e:
                    print(f"❌ Error creando worksheet: {e}")
                    # Intentar usar worksheet existente
                    try:
                        if self.spreadsheet:
                            worksheets = self.spreadsheet.worksheets()
                            if worksheets:
                                self.worksheet = worksheets[0]
                                print(f"✅ Usando worksheet existente: {self.worksheet.title}")
                            else:
                                print("❌ No hay worksheets disponibles")
                                return False
                        else:
                            print("❌ Spreadsheet no inicializado")
                            return False
                    except Exception as e2:
                        print(f"❌ Error accediendo a worksheets: {e2}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando spreadsheet: {e}")
            return False
    
    def log_trade(self, datetime_str: str, symbol: str, direction: str, 
                  entry_price: float, result: str, pnl: float, 
                  quantity: float = 0, amount: float = 0, 
                  strategy: str = "breakout", confidence: float = 0,
                  ai_validation: str = "N/A", balance: float = 0) -> bool:
        """
        Registrar operación en Google Sheets
        
        Args:
            datetime_str: Fecha y hora (formato: "2025-08-05 22:15:30")
            symbol: Símbolo del activo (ej: "BTCUSDT")
            direction: Dirección de la operación ("BUY" o "SELL")
            entry_price: Precio de entrada
            result: Resultado de la operación ("EXITOSA", "PENDIENTE", etc.)
            pnl: Profit/Loss de la operación
            quantity: Cantidad operada
            amount: Monto total
            strategy: Estrategia utilizada
            confidence: Confianza de la señal (%)
            ai_validation: Validación de IA
            balance: Balance actual
            
        Returns:
            True si se registró correctamente
        """
        try:
            if not self.worksheet:
                if not self.open_or_create_spreadsheet():
                    print("❌ No se pudo abrir spreadsheet")
                    return False
            
            # Parsear datetime (soporta tanto formato ISO como simple)
            try:
                # Intentar formato ISO primero
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Intentar formato simple
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Si falla, usar datetime actual
                    dt = datetime.now()
            
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
            
            # Preparar datos para la fila
            row_data = [
                date_str,                           # Fecha
                time_str,                           # Hora
                symbol,                             # Símbolo
                direction,                          # Dirección
                f"${entry_price:,.2f}",            # Precio Entrada
                f"{quantity:.6f}",                  # Cantidad
                f"${amount:.2f}",                  # Monto
                strategy,                           # Estrategia
                f"{confidence:.1f}%",              # Confianza
                ai_validation,                      # IA Validación
                result,                            # Resultado
                f"${pnl:.2f}",                    # P&L
                f"${balance:.2f}"                 # Balance
            ]
            
            # Agregar fila
            if self.worksheet:
                self.worksheet.append_row(row_data)
                print(f"✅ Operación registrada en Google Sheets: {direction} {symbol} @ ${entry_price:,.2f}")
                return True
            else:
                print("❌ Worksheet no inicializado")
                return False
            
        except Exception as e:
            print(f"❌ Error registrando operación en Google Sheets: {e}")
            return False
    
    def log_trade_dict(self, trade_data: Dict) -> bool:
        """
        Registrar operación usando diccionario
        
        Args:
            trade_data: Diccionario con datos de la operación
            
        Returns:
            True si se registró correctamente
        """
        try:
            # Validar campos requeridos
            required_fields = ['symbol', 'side', 'price', 'amount']
            for field in required_fields:
                if field not in trade_data:
                    print(f"❌ Error: Campo requerido '{field}' no encontrado en trade_data")
                    return False
            
            # Extraer datos del diccionario
            datetime_str = trade_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            symbol = trade_data.get('symbol', 'BTCUSDT')
            direction = trade_data.get('side', 'BUY')  # Cambiado de 'signal' a 'side'
            entry_price = trade_data.get('price', 0)
            quantity = trade_data.get('quantity', 0)
            amount = trade_data.get('amount', 0)
            strategy = trade_data.get('strategy', 'breakout')
            confidence = trade_data.get('confidence', 0)
            
            # Mejorar manejo de validación de IA
            ai_validation = trade_data.get('ai_validation', 'N/A')
            if ai_validation == 'N/A' and 'ai_response' in trade_data:
                ai_response = trade_data.get('ai_response', '')
                if ai_response:
                    # Extraer solo la primera parte de la respuesta de IA
                    if 'CONFIRMADO' in ai_response.upper():
                        ai_validation = 'CONFIRMADO'
                    elif 'RECHAZADO' in ai_response.upper():
                        ai_validation = 'RECHAZADO'
                    elif 'CAUTELA' in ai_response.upper():
                        ai_validation = 'CAUTELA'
                    else:
                        ai_validation = ai_response[:50] + '...' if len(ai_response) > 50 else ai_response
            
            pnl = trade_data.get('pnl', 0)
            balance = trade_data.get('balance', 100)
            
            # Determinar resultado
            if pnl > 0:
                result = "GANANCIA"
            elif pnl < 0:
                result = "PÉRDIDA"
            else:
                result = "PENDIENTE"
            
            return self.log_trade(
                datetime_str=datetime_str,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                result=result,
                pnl=pnl,
                quantity=quantity,
                amount=amount,
                strategy=strategy,
                confidence=confidence,
                ai_validation=ai_validation,
                balance=balance
            )
            
        except Exception as e:
            print(f"❌ Error procesando datos de operación: {e}")
            return False
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """Obtener URL del spreadsheet"""
        if self.spreadsheet:
            return self.spreadsheet.url
        return None

# Función de conveniencia para uso rápido
def log_trade(datetime_str: str, symbol: str, direction: str, 
              entry_price: float, result: str, pnl: float, **kwargs) -> bool:
    """
    Función de conveniencia para registrar operación
    
    Args:
        datetime_str: Fecha y hora
        symbol: Símbolo del activo
        direction: Dirección ("BUY" o "SELL")
        entry_price: Precio de entrada
        result: Resultado de la operación
        pnl: Profit/Loss
        **kwargs: Datos adicionales
        
    Returns:
        True si se registró correctamente
    """
    logger = SheetsLogger()
    return logger.log_trade(datetime_str, symbol, direction, entry_price, result, pnl, **kwargs)

# Función principal para el bot - SOLO GOOGLE SHEETS
def log_trade_to_sheet(trade_data: Dict) -> bool:
    """
    Función principal para registrar operaciones del bot en Google Sheets
    
    Args:
        trade_data: Diccionario con datos de la operación
        
    Returns:
        True si se registró correctamente
    """
    try:
        # Usar la instancia global si está disponible
        global sheets_logger
        if sheets_logger is None:
            # Crear nueva instancia si no existe
            if init_sheets_logger():
                sheets_logger = get_sheets_logger()
            else:
                print("❌ No se pudo inicializar Google Sheets Logger")
                return False
        
        if sheets_logger and sheets_logger.worksheet:
            success = sheets_logger.log_trade_dict(trade_data)
            if success:
                print("✅ Operación registrada exitosamente en Google Sheets")
                return True
            else:
                print("❌ Error registrando operación en Google Sheets")
                return False
        else:
            print("❌ No se pudo configurar Google Sheets")
            return False
        
    except Exception as e:
        print(f"❌ Error en log_trade_to_sheet: {e}")
        return False

# Función de exportación a CSV (solo cuando se solicita explícitamente)
def export_trades_to_csv(trades_data: list, filename: str = "data/trades_export.csv") -> bool:
    """
    Exportar operaciones a CSV (solo cuando se solicita explícitamente)
    
    Args:
        trades_data: Lista de diccionarios con datos de operaciones
        filename: Nombre del archivo CSV
        
    Returns:
        True si se exportó correctamente
    """
    try:
        # Asegurar que el directorio existe
        os.makedirs('data', exist_ok=True)
        
        # Preparar headers
        headers = [
            'Fecha', 'Hora', 'Símbolo', 'Dirección', 'Precio Entrada',
            'Cantidad', 'Monto', 'Estrategia', 'Confianza', 
            'IA Validación', 'Resultado', 'P&L', 'Balance'
        ]
        
        # Escribir en CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for trade in trades_data:
                # Preparar datos
                datetime_str = trade.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
                
                symbol = trade.get('symbol', 'BTCUSDT')
                direction = trade.get('side', 'BUY')
                entry_price = trade.get('price', 0)
                quantity = trade.get('quantity', 0)
                amount = trade.get('amount', 0)
                strategy = trade.get('strategy', 'breakout')
                confidence = trade.get('confidence', 0)
                ai_validation = trade.get('ai_validation', 'N/A')
                pnl = trade.get('pnl', 0)
                balance = trade.get('balance', 100)
                
                # Determinar resultado
                if pnl > 0:
                    result = "GANANCIA"
                elif pnl < 0:
                    result = "PÉRDIDA"
                else:
                    result = "PENDIENTE"
                
                # Preparar fila
                row_data = [
                    date_str, time_str, symbol, direction, f"${entry_price:,.2f}",
                    f"{quantity:.6f}", f"${amount:.2f}", strategy, f"{confidence:.1f}%",
                    ai_validation, result, f"${pnl:.2f}", f"${balance:.2f}"
                ]
                
                writer.writerow(row_data)
        
        print(f"✅ Operaciones exportadas a CSV: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error exportando a CSV: {e}")
        return False

# Instancia global para uso en el bot
sheets_logger = None

def init_sheets_logger(spreadsheet_name: str = "Trading Bot Log") -> bool:
    """Inicializar logger de Google Sheets"""
    global sheets_logger
    try:
        sheets_logger = SheetsLogger(spreadsheet_name)
        if sheets_logger.open_or_create_spreadsheet():
            print("✅ Google Sheets Logger inicializado")
            return True
        else:
            print("❌ Error inicializando Google Sheets Logger")
            return False
    except Exception as e:
        print(f"❌ Error configurando Google Sheets Logger: {e}")
        return False

def get_sheets_logger() -> Optional[SheetsLogger]:
    """Obtener instancia del logger"""
    return sheets_logger 