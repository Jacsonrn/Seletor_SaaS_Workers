import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

# Configura o PATH para os scripts Cython
SELETOR_PATH = r"C:\Users\Jacson\Documents\Repositorios\seletor_saas"
if SELETOR_PATH not in sys.path:
    sys.path.insert(0, SELETOR_PATH)
if os.name == 'nt':
    try:
        os.add_dll_directory(SELETOR_PATH)
    except Exception:
        pass

import diretor_windows_cpu_core
import narrador_cpu_core
import cameraman_cpu_core
import montador_windows_cpu_core

app = FastAPI(title="Worker Seletor SaaS (PC B)")

def executar_pipeline_ia(config_dict: dict):
    projeto_id = config_dict.get('projeto_id')
    print(f"\n=======================================================")
    print(f"[WORKER FastAPI] Iniciando Processamento (Proj: {projeto_id})")
    print(f"=======================================================")
    try:
        print("\n>>> [PASSO 1/4] INICIANDO DIRETOR...")
        diretor_windows_cpu_core.main(config_dict)
        
        print("\n>>> [PASSO 2/4] INICIANDO NARRADOR...")
        narrador_cpu_core.main(config_dict)
        
        print("\n>>> [PASSO 3/4] INICIANDO CAMERAMAN...")
        cameraman_cpu_core.main(config_dict)
        
        print("\n>>> [PASSO 4/4] INICIANDO MONTADOR...")
        montador_windows_cpu_core.main(config_dict)
        
        print(f"\n[WORKER FastAPI] SUCESSO! Projeto {projeto_id} concluído.")
        print(f"=======================================================")
        
        # Aqui no futuro podemos fazer um requests.post() de volta para o Django 
        # avisando que o vídeo terminou e enviando a URL de download.
        
    except Exception as e:
        print(f"\n[WORKER ERRO FATAL] Falha no projeto {projeto_id}: {e}")

@app.post("/api/processar")
async def processar_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    projeto_id: int = Form(...),
    api_key_gemini: str = Form(""),
    persona_ativa: str = Form("historiador"),
    prompt_especial: str = Form(""),
    formato_saida: str = Form("16:9"),
    duracao_segundos: float = Form(60.0),
    marca_dagua: str = Form(""),
    limitar_shorts: bool = Form(True),
    barra_curiosidade: bool = Form(True),
    animacao_legenda: bool = Form(True),
    cor_fundo_tarja: str = Form("black"),
    cor_fonte_tarja: str = Form("#FFFFFF"),
    fundo_video: str = Form("BORRAO"),
    fonte_audio: str = Form("original"),
    tempo_fadein_audio: float = Form(1.0),
    ducking_audio: bool = Form(False),
    efeito_halation: bool = Form(False),
    halation_vermelho: float = Form(2.0),
    halation_desfoque: float = Form(10.0),
    nitidez_cas: bool = Form(True),
    forca_nitidez: float = Form(0.8),
    resolucao_upscale: bool = Form(False),
    tempo_oscilacao_zoom: float = Form(10.0),
    opacidade_logo: float = Form(0.5),
    zoom_respiratorio: bool = Form(True),
    criatividade: int = Form(70)
):
    # O Worker precisa salvar o vídeo num diretório temporário próprio dele
    # (Pois ele roda em outro computador)
    work_dir = os.path.join(SELETOR_PATH, "worker_storage", f"projeto_{projeto_id}")
    os.makedirs(work_dir, exist_ok=True)
    
    video_path = os.path.join(work_dir, "upload_video.mp4")
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
        
    # Recria o config_dict no lado do Worker
    config_dict = {
        'projeto_id': projeto_id,
        'video_original': video_path,
        'diretriz_dir': work_dir,
        'api_key_gemini': api_key_gemini,
        'persona_ativa': persona_ativa,
        'prompt_especial': prompt_especial,
        'formato_saida': formato_saida,
        'duracao_segundos': duracao_segundos,
        'marca_dagua': marca_dagua,
        'limitar_shorts': limitar_shorts,
        'barra_curiosidade': barra_curiosidade,
        'animacao_legenda': animacao_legenda,
        'cor_fundo_tarja': cor_fundo_tarja,
        'cor_fonte_tarja': cor_fonte_tarja,
        'fundo_video': fundo_video,
        'fonte_audio': fonte_audio,
        'tempo_fadein_audio': tempo_fadein_audio,
        'ducking_audio': ducking_audio,
        'efeito_halation': efeito_halation,
        'halation_vermelho': halation_vermelho,
        'halation_desfoque': halation_desfoque,
        'nitidez_cas': nitidez_cas,
        'forca_nitidez': forca_nitidez,
        'resolucao_upscale': resolucao_upscale,
        'tempo_oscilacao_zoom': tempo_oscilacao_zoom,
        'opacidade_logo': opacidade_logo,
        'zoom_respiratorio': zoom_respiratorio,
        'criatividade': criatividade,
    }
    
    # Manda rodar no background do FastAPI (Ele devolve o return abaixo instantaneamente pro Django)
    background_tasks.add_task(executar_pipeline_ia, config_dict)
    
    return {"status": "ok", "mensagem": f"Vídeo de {video_file.size} bytes recebido. Processamento iniciado no background."}

# Para rodar o Worker (No Computador B):
# uvicorn api_worker:app --host 0.0.0.0 --port 8001
