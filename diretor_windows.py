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

import diretor_windows_core

if __name__ == '__main__':
    if hasattr(diretor_windows_core, 'main'):
        diretor_windows_core.main()
