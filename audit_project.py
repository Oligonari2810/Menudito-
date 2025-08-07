#!/usr/bin/env python3
"""
🔍 AUDITORÍA COMPLETA DEL PROYECTO
Revisión exhaustiva para descubrir errores
"""

import os
import sys
import ast
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectAuditor:
    """Auditor completo del proyecto"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.files_checked = 0
        self.python_files = []
        
    def find_python_files(self):
        """Encontrar todos los archivos Python"""
        logger.info("🔍 Buscando archivos Python...")
        
        for root, dirs, files in os.walk('.'):
            # Ignorar directorios comunes
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'logs']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.python_files.append(file_path)
        
        logger.info(f"✅ Encontrados {len(self.python_files)} archivos Python")
        return self.python_files
    
    def check_syntax_errors(self, file_path):
        """Verificar errores de sintaxis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar sintaxis
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.errors.append(f"❌ {file_path}: Error de sintaxis - {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Error leyendo archivo - {e}")
            return False
    
    def check_imports(self, file_path):
        """Verificar imports problemáticos"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'sys' and 'sys.exit' not in content:
                            self.warnings.append(f"⚠️ {file_path}: Import 'sys' no usado")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module == 'sys' and 'exit' in [n.name for n in node.names]:
                        if 'sys.exit' not in content:
                            self.warnings.append(f"⚠️ {file_path}: Import 'sys.exit' no usado")
            
            return True
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Error verificando imports - {e}")
            return False
    
    def check_main_files(self):
        """Verificar archivos principales"""
        logger.info("🔍 Verificando archivos principales...")
        
        main_files = [
            'minimal_working_bot.py',
            'deploy_render.py',
            'main_survivor.py',
            'simple_bot.py'
        ]
        
        for file in main_files:
            if os.path.exists(file):
                logger.info(f"✅ {file}: Existe")
                
                # Verificar sintaxis
                if not self.check_syntax_errors(file):
                    continue
                
                # Verificar imports
                self.check_imports(file)
                
                # Verificar contenido específico
                self.check_file_content(file)
            else:
                self.warnings.append(f"⚠️ {file}: No encontrado")
    
    def check_file_content(self, file_path):
        """Verificar contenido específico del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar problemas comunes
            if 'ProfessionalTradingBot' in content:
                logger.info(f"✅ {file_path}: Usa ProfessionalTradingBot")
            
            if 'MinimalTradingBot' in content:
                self.warnings.append(f"⚠️ {file_path}: Usa clase antigua MinimalTradingBot")
            
            if 'time.sleep(60)' in content:
                logger.info(f"✅ {file_path}: Ciclos de 60 segundos")
            
            if 'time.sleep(120)' in content:
                self.warnings.append(f"⚠️ {file_path}: Ciclos lentos de 120 segundos")
            
            # Verificar variables de entorno
            env_vars = ['BINANCE_API_KEY', 'TELEGRAM_BOT_TOKEN', 'GOOGLE_SHEETS_CREDENTIALS']
            for var in env_vars:
                if var in content:
                    logger.info(f"✅ {file_path}: Usa {var}")
            
            # Verificar manejo de errores
            if 'try:' in content and 'except:' in content:
                logger.info(f"✅ {file_path}: Manejo de errores presente")
            else:
                self.warnings.append(f"⚠️ {file_path}: Sin manejo de errores")
                
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Error verificando contenido - {e}")
    
    def check_configuration_files(self):
        """Verificar archivos de configuración"""
        logger.info("🔍 Verificando archivos de configuración...")
        
        config_files = [
            'requirements.txt',
            'render.yaml',
            'runtime.txt',
            '.python-version'
        ]
        
        for file in config_files:
            if os.path.exists(file):
                logger.info(f"✅ {file}: Existe")
                self.check_config_content(file)
            else:
                self.warnings.append(f"⚠️ {file}: No encontrado")
    
    def check_config_content(self, file_path):
        """Verificar contenido de archivos de configuración"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path == 'requirements.txt':
                required_deps = ['requests', 'gspread', 'google-auth']
                for dep in required_deps:
                    if dep in content:
                        logger.info(f"✅ {file_path}: Incluye {dep}")
                    else:
                        self.warnings.append(f"⚠️ {file_path}: Falta {dep}")
            
            elif file_path == 'render.yaml':
                if 'python3' in content:
                    logger.info(f"✅ {file_path}: Configurado para Python 3")
                if 'deploy_render.py' in content:
                    logger.info(f"✅ {file_path}: Usa deploy_render.py")
            
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Error verificando configuración - {e}")
    
    def check_duplicate_files(self):
        """Verificar archivos duplicados o conflictivos"""
        logger.info("🔍 Verificando archivos duplicados...")
        
        # Verificar múltiples bots
        bot_files = [
            'minimal_working_bot.py',
            'simple_bot.py',
            'main_survivor.py'
        ]
        
        existing_bots = [f for f in bot_files if os.path.exists(f)]
        if len(existing_bots) > 1:
            self.warnings.append(f"⚠️ Múltiples bots encontrados: {existing_bots}")
            logger.warning("⚠️ Esto puede causar confusión sobre cuál se ejecuta")
    
    def check_unused_files(self):
        """Verificar archivos no utilizados"""
        logger.info("🔍 Verificando archivos no utilizados...")
        
        # Archivos que probablemente no se usan
        potentially_unused = [
            'debug_sheets.py',
            'test_bot_sheets.py',
            'check_sheet_names.py',
            'test_render_credentials.py',
            'test_sheets_connection.py',
            'convert_credentials.py',
            'test_google_sheets.py',
            'import_telegram_trades.py',
            'compare_trades.py',
            'import_single_trade.py',
            'free_tier_handler.py',
            'test_bot_startup.py',
            'config_survivor_final.py',
            'daily_evaluation.py',
            'sheets_logger.py'
        ]
        
        for file in potentially_unused:
            if os.path.exists(file):
                self.warnings.append(f"⚠️ {file}: Posiblemente no usado")
    
    def run_audit(self):
        """Ejecutar auditoría completa"""
        logger.info("🚀 INICIANDO AUDITORÍA COMPLETA DEL PROYECTO")
        logger.info("=" * 60)
        
        # Encontrar archivos Python
        self.find_python_files()
        
        # Verificar archivos principales
        self.check_main_files()
        
        # Verificar configuración
        self.check_configuration_files()
        
        # Verificar duplicados
        self.check_duplicate_files()
        
        # Verificar archivos no usados
        self.check_unused_files()
        
        # Resumen
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumen de la auditoría"""
        logger.info("\n📊 RESUMEN DE LA AUDITORÍA")
        logger.info("=" * 60)
        
        logger.info(f"📁 Archivos Python encontrados: {len(self.python_files)}")
        logger.info(f"❌ Errores encontrados: {len(self.errors)}")
        logger.info(f"⚠️ Advertencias encontradas: {len(self.warnings)}")
        
        if self.errors:
            logger.error("\n❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                logger.error(f"  {error}")
        
        if self.warnings:
            logger.warning("\n⚠️ ADVERTENCIAS:")
            for warning in self.warnings:
                logger.warning(f"  {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("✅ No se encontraron errores críticos")
        else:
            logger.info("\n🔧 RECOMENDACIONES:")
            if self.errors:
                logger.info("  • Corregir errores de sintaxis")
            if len([w for w in self.warnings if 'Múltiples bots' in w]) > 0:
                logger.info("  • Decidir qué bot usar y eliminar los demás")
            if len([w for w in self.warnings if 'no usado' in w]) > 0:
                logger.info("  • Limpiar archivos no utilizados")
            if len([w for w in self.warnings if 'MinimalTradingBot' in w]) > 0:
                logger.info("  • Actualizar referencias a clases antiguas")

def main():
    """Función principal"""
    auditor = ProjectAuditor()
    auditor.run_audit()

if __name__ == "__main__":
    main()
