import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

if os.name == 'nt':
    try:
        os.add_dll_directory(script_dir)
    except Exception:
        pass
    os.environ['PATH'] = script_dir + os.pathsep + os.environ['PATH']

import montador_windows_cpu_core

if __name__ == '__main__':
    # O Cython executa automaticamente o escopo global quando importado, 
    # mas caso haja uma funcao main(), podemos chamar:
    if hasattr(montador_windows_cpu_core, 'main'):
        montador_windows_cpu_core.main()
