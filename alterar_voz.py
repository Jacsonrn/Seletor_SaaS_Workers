import sys
import os

# FIX CRITICO: Garante que o diretorio do script esteja no sys.path
# O Python Embed muitas vezes nao adiciona o diretorio atual automaticamente
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

try:
    import alterar_voz_core
except ImportError as e:
    print(f"\n>> [ERRO FATAL] Nao foi possivel importar o modulo 'alterar_voz_core'.")
    print(f">> Detalhe do erro: {e}")
    print(f">> Diretorio atual (CWD): {os.getcwd()}")
    print(f">> sys.path: {sys.path}")
    print(f">> Arquivos .pyd encontrados nesta pasta:")
    found = False
    for f in os.listdir('.'):
        if f.endswith('.pyd'):
            print(f"   - {f}")
            found = True
    if not found:
        print("   (Nenhum arquivo .pyd encontrado)")
    print("\n")
    sys.exit(1)

if __name__ == "__main__":
    alterar_voz_core.main()
