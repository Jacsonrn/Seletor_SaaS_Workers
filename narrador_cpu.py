import sys
import os

# Garante que a pasta atual está no PYTHONPATH para encontrar a extensão compilada (.pyd)
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Resolve possíveis problemas de carregamento de bibliotecas C no Windows
if os.name == 'nt':
    try:
        os.add_dll_directory(script_dir)
    except Exception:
        pass
    os.environ['PATH'] = script_dir + os.pathsep + os.environ.get('PATH', '')

import narrador_cpu_core

if __name__ == '__main__':
    # Chama a função principal de extração passando os argumentos originais do sistema (API Key, Diretórios, etc)
    if hasattr(narrador_cpu_core, 'main'):
        narrador_cpu_core.main()
    else:
        print("[ERRO] A função 'main' não foi encontrada no módulo compilado.")
