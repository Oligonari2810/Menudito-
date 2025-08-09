#!/usr/bin/env python3
"""
🧪 TEST: Validación de imports de typing
Verifica que todos los archivos tengan los imports correctos de typing
"""

import os
import sys
import ast
from typing import List, Dict, Any, Optional

def check_typing_imports(file_path: str) -> Dict[str, Any]:
    """Verificar imports de typing en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsear el archivo
        tree = ast.parse(content)
        
        # Buscar imports de typing
        typing_imports = []
        has_typing_import = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'typing':
                    has_typing_import = True
                    for alias in node.names:
                        typing_imports.append(alias.name)
        
        # Verificar que tenga los imports necesarios
        required_imports = ['Any', 'Dict', 'List', 'Optional']
        missing_imports = [imp for imp in required_imports if imp not in typing_imports]
        
        return {
            'file': file_path,
            'has_typing_import': has_typing_import,
            'typing_imports': typing_imports,
            'missing_imports': missing_imports,
            'valid': len(missing_imports) == 0
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'valid': False
        }

def test_all_files() -> Dict[str, Any]:
    """Testear todos los archivos Python del proyecto"""
    python_files = []
    
    # Buscar archivos Python
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    results = []
    all_valid = True
    
    for file_path in python_files:
        result = check_typing_imports(file_path)
        results.append(result)
        
        if not result['valid']:
            all_valid = False
            print(f"❌ {file_path}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            else:
                print(f"   Missing imports: {result['missing_imports']}")
        else:
            print(f"✅ {file_path}")
    
    return {
        'total_files': len(python_files),
        'valid_files': len([r for r in results if r['valid']]),
        'invalid_files': len([r for r in results if not r['valid']]),
        'all_valid': all_valid,
        'results': results
    }

def main():
    """Función principal"""
    print("🧪 Test: Validación de imports de typing")
    print("=" * 50)
    
    results = test_all_files()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    print(f"📁 Archivos totales: {results['total_files']}")
    print(f"✅ Archivos válidos: {results['valid_files']}")
    print(f"❌ Archivos inválidos: {results['invalid_files']}")
    
    if results['all_valid']:
        print("\n🎉 ¡Todos los imports de typing son correctos!")
        return 0
    else:
        print("\n❌ Algunos archivos tienen imports de typing incorrectos")
        print("🔧 Revisar los archivos marcados con ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
