import sys
import os
import subprocess

# Wrapper simples para o gdown baixar um arquivo especifico
# Uso: python download_drive_file.py <file_id> <caminho_destino>

try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

def main():
    if len(sys.argv) < 3:
        print("Erro: Args")
        return

    file_id = sys.argv[1]
    dest = sys.argv[2]
    
    url = f'https://drive.google.com/uc?id={file_id}'
    try:
        gdown.download(url, dest, quiet=False)
        print("SUCESSO")
    except Exception as e:
        print(f"ERRO: Falha no download. Verifique se o arquivo no Google Drive esta compartilhado como 'Qualquer pessoa com o link'.")
        print(f"Detalhes: {e}")
        # Remove arquivo parcial se existir
        if os.path.exists(dest):
            try: os.remove(dest)
            except: pass

if __name__ == "__main__":
    main()