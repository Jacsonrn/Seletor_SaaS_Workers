import sys
import os

# FIX CRITICO: Garante que o diretorio do script esteja no sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# FIX: Adiciona o diretorio atual ao PATH de DLLs (Necessario para extensoes MinGW/GCC no Windows)
if os.name == 'nt':
    try:
        os.add_dll_directory(script_dir)
    except Exception:
        pass
    os.environ['PATH'] = script_dir + os.pathsep + os.environ['PATH']

import gerar_imagens_core

if __name__ == "__main__":
    gerar_imagens_core.main()