# ==============================================================================
# CÉLULA ÚNICA DE EXTRAÇÃO PARA O GOOGLE COLAB
# Copie e cole este código inteiro em uma célula do seu Jupyter Notebook no Colab
# ==============================================================================

import os
import sys
import cv2
import time
import numpy as np
import requests
import subprocess
import shutil
from tqdm import tqdm

# ==============================================================================
# FASE 3: INSTALAÇÃO DE DEPENDÊNCIAS E FASE 2: MONTAGEM DO DRIVE
# ==============================================================================
try:
    from google.colab import drive, files
    print(">> Montando Google Drive...")
    drive.mount('/content/drive')
except ImportError:
    print(">> AVISO: Não estamos no Google Colab. Ignorando montagem do Drive.")

# ==============================================================================
# CONFIGURAÇÕES DE ENTRADA E SAÍDA (Edite conforme suas pastas no Drive)
# ==============================================================================
PASTA_INPUT = "/content/drive/MyDrive/Extracao"
PASTA_OUTPUT_BASE = "/content/drive/MyDrive/Seletor Assets Midia"
VIDEO_PATH = os.path.join(PASTA_INPUT, "video_longo.mp4")
REF_IMG_PATH = os.path.join(PASTA_INPUT, "referencia.jpeg")

print("==================================================================")
NOME_PASTA = input(">> Digite o nome da nova pasta para salvar os resultados: ").strip()
if not NOME_PASTA:
    NOME_PASTA = "Cortes_Finalizados"

OUTPUT_DIR = os.path.join(PASTA_OUTPUT_BASE, NOME_PASTA)
ZIP_PATH = os.path.join(PASTA_OUTPUT_BASE, f"{NOME_PASTA}.zip")

TIPO_SAIDA = input(">> Você deseja exportar em 'videos' ou 'fotos'? [videos/fotos]: ").strip().lower()
while TIPO_SAIDA not in ['videos', 'fotos']:
    TIPO_SAIDA = input(">> Opção inválida. Digite 'videos' ou 'fotos': ").strip().lower()

INTERVALO_FOTOS = 1.0
UPSCALE_FOTOS = False
if TIPO_SAIDA == 'fotos':
    val = input(">> Qual o intervalo mínimo entre as fotos (em segundos)? [Padrão: 1.0]: ").strip()
    if val:
        try:
            INTERVALO_FOTOS = float(val)
        except ValueError:
            print("   Valor inválido. Usando 1.0s por padrão.")
            
    resp_up = input(">> Deseja aplicar Upscale de IA (2x) nas fotos extraídas? [s/n]: ").strip().lower()
    if resp_up == 's':
        UPSCALE_FOTOS = True
print("==================================================================")

# Parâmetros da ferramenta (equivalentes aos da sua interface em C++)
FRAME_SKIP = 10         # A cada quantos frames a IA busca o rosto (Velocidade)
MIN_DURATION = 2.0      # Duração mínima do corte em segundos
MAX_DURATION = 60.0     # Duração máxima do corte em segundos
GAP_TOLERANCE = 2.0     # Tolerância para unir cortes muito próximos
SIMILARITY_THRESHOLD = 0.45  # Rigor do reconhecimento (Padrão original era 0.363. Maior = mais rigoroso)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# PREPARAÇÃO DA INTELIGÊNCIA ARTIFICIAL (Modelos OpenCV DNN)
# ==============================================================================
def baixar_modelo_se_necessario(url, destino):
    if not os.path.exists(destino):
        print(f">> Baixando IA: {os.path.basename(destino)}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destino, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        else:
            print(f"ERRO ao baixar modelo: {response.status_code}")

model_dir = "/content/models"
os.makedirs(model_dir, exist_ok=True)

face_det_model = os.path.join(model_dir, "face_detection_yunet_2023mar.onnx")
face_rec_model = os.path.join(model_dir, "face_recognition_sface_2021dec.onnx")
url_det = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
url_rec = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

baixar_modelo_se_necessario(url_det, face_det_model)
baixar_modelo_se_necessario(url_rec, face_rec_model)

print(">> Inicializando Motor Visual...")

# Configuração para usar GPU (CUDA) se disponível no ambiente
backend_id = cv2.dnn.DNN_BACKEND_OPENCV
target_id = cv2.dnn.DNN_TARGET_CPU

try:
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print("   [!] GPU CUDA detectada. Ativando aceleração de hardware na IA...")
        backend_id = cv2.dnn.DNN_BACKEND_CUDA
        target_id = cv2.dnn.DNN_TARGET_CUDA
    else:
        print("   [!] GPU não alocada nesta sessão do Colab. Usando CPU.")
except AttributeError:
    print("\n   [AVISO IMPORTANTE] O OpenCV nativo do Colab não possui suporte a GPU (CUDA).")
    print("   O motor visual e de corte foi automaticamente redirecionado para a CPU (Processador).")
    if UPSCALE_FOTOS:
        print("   -> ATENÇÃO: Fazer Upscale de imagens na CPU demorará muito mais do que o normal!\n")
    pass

detector = cv2.FaceDetectorYN.create(face_det_model, "", (320, 320), 0.6, 0.3, 5000, backend_id, target_id)
recognizer = cv2.FaceRecognizerSF.create(face_rec_model, "", backend_id, target_id)

# Inicializa o Motor de Upscale se solicitado
sr = None
if UPSCALE_FOTOS:
    try:
        from cv2 import dnn_superres
    except ImportError:
        print(">> Instalando pacote necessário para o Upscaler (opencv-contrib-python-headless)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-contrib-python-headless"])
        from cv2 import dnn_superres
        
    # FSRCNN_x2.pb é incrivelmente rápido e leve para a GPU.
    sr_model_path = os.path.join(model_dir, "FSRCNN_x2.pb")
    url_sr = "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x2.pb"
    baixar_modelo_se_necessario(url_sr, sr_model_path)
    
    print(">> Inicializando Motor de Upscale (FSRCNN x2)...")
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(sr_model_path)
    sr.setModel("fsrcnn", 2)
    sr.setPreferableBackend(backend_id)
    sr.setPreferableTarget(target_id)

# ==============================================================================
# EXTRAÇÃO DA REFERÊNCIA ALVO (A foto da pessoa)
# ==============================================================================
ref_img = cv2.imread(REF_IMG_PATH)
if ref_img is None:
    raise ValueError(f"ERRO: Imagem de referência não encontrada no caminho: {REF_IMG_PATH}")

h, w, _ = ref_img.shape
detector.setInputSize((w, h))
_, faces = detector.detect(ref_img)

if faces is None:
    raise ValueError("Nenhum rosto detectado na foto de referência. Escolha outra foto.")

face_align = recognizer.alignCrop(ref_img, faces[0])
ref_feat = recognizer.feature(face_align)

# ==============================================================================
# MAPEAMENTO DO VÍDEO (A Busca Frame a Frame)
# ==============================================================================
print(f">> Assistindo ao vídeo: {os.path.basename(VIDEO_PATH)}")
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise ValueError(f"ERRO: Vídeo não encontrado ou corrompido: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

timestamps_found = []
frame_count = 0
saved_count = 0
last_saved_time = -INTERVALO_FOTOS

pbar_analise = tqdm(total=total_frames, desc="Analisando frames", unit="frame")
while True:
    ret, frame = cap.read()
    if not ret: break
    
    if frame_count % FRAME_SKIP == 0:
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        h, w, _ = small_frame.shape
        detector.setInputSize((w, h))
        _, faces = detector.detect(small_frame)
        
        if faces is not None:
            for face in faces:
                face_align = recognizer.alignCrop(small_frame, face)
                feat = recognizer.feature(face_align)
                score = recognizer.match(ref_feat, feat, cv2.FaceRecognizerSF_FR_COSINE)
                
                if score >= SIMILARITY_THRESHOLD:  # Limiar Cosine (Pessoa encontrada!)
                    current_time = frame_count / fps
                    if TIPO_SAIDA == 'videos':
                        timestamps_found.append(current_time)
                    else:
                        if (current_time - last_saved_time) >= INTERVALO_FOTOS:
                            foto_final = frame
                            if UPSCALE_FOTOS and sr is not None:
                                foto_final = sr.upsample(frame)
                            nome_foto = f"foto_{saved_count:03d}_{int(current_time)}s.jpeg"
                            cv2.imwrite(os.path.join(OUTPUT_DIR, nome_foto), foto_final)
                            timestamps_found.append(current_time)
                            saved_count += 1
                            last_saved_time = current_time
                    break

    frame_count += 1
    pbar_analise.update(1)

pbar_analise.close()
cap.release()

# ==============================================================================
# A TESOURA (Calculando Segmentos e Cortando ou Finalizando)
# ==============================================================================
if not timestamps_found:
    print(">> FIM: O personagem da foto não foi encontrado no vídeo.")
    sys.exit()

if TIPO_SAIDA == 'videos':
    print(">> Calculando pontos de corte...")
    segments = []
    start_seg = timestamps_found[0]
    last_time = timestamps_found[0]
    
    for t in timestamps_found[1:]:
        if t - last_time <= GAP_TOLERANCE:
            last_time = t
        else:
            segments.append([start_seg, last_time])
            start_seg = t
            last_time = t
    segments.append([start_seg, last_time])
    
    print(f">> Iniciando FFmpeg nativo do Colab: Extraindo {len(segments)} trechos...")
    count = 0
    pbar_cortes = tqdm(total=len(segments), desc="Cortando vídeos", unit="video")
    for seg in segments:
        start = max(0.0, seg[0] - 0.5)
        end = min(duration, seg[1] + 0.5)
        duracao = end - start
        
        # Aplica lógica de limites (Mínimo e Máximo) idêntica ao VideoCutter.cpp
        if MIN_DURATION > 0 and duracao < MIN_DURATION:
            diff = MIN_DURATION - duracao
            start = max(0.0, start - (diff / 2.0))
            end += (diff / 2.0)
            duracao = end - start
            
        duracaoFinal = min(duracao, MAX_DURATION) if MAX_DURATION > 0 else duracao
            
        nome_saida = f"corte_{count}.mp4"
        path_saida = os.path.join(OUTPUT_DIR, nome_saida)
        
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-t", str(duracaoFinal),
            "-i", VIDEO_PATH,
            "-c:v", "copy",
            "-c:a", "copy",
            path_saida
        ]
        
        # Roda o FFmpeg em background
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        count += 1
        pbar_cortes.update(1)
    
    pbar_cortes.close()
else:
    print(f">> FIM DA EXTRAÇÃO: {saved_count} fotos foram extraídas e salvas com sucesso.")
    count = saved_count # Reutiliza a variável count para o log final

# ==============================================================================
# FASE 3: EXPORTAÇÃO (Compactando para ZIP e Baixando)
# ==============================================================================
print(f">> Compactando {count} vídeos em um arquivo ZIP...")
shutil.make_archive(OUTPUT_DIR, 'zip', OUTPUT_DIR)

print("==================================================================")
print(f"[SUCESSO] Todos os {count} clipes foram gerados na pasta:")
print(OUTPUT_DIR)
print(f"Arquivo ZIP salvo em: {ZIP_PATH}")
print("==================================================================")

try:
    print(">> Iniciando download automático do ZIP...")
    files.download(ZIP_PATH)
except Exception as e:
    print(">> O download automático só funciona diretamente no navegador do Colab.")