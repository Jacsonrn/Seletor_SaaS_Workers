import sys
import cv2
import os
import time
import numpy as np

def baixar_modelo_se_necessario(url, destino):
    if not os.path.exists(destino):
        print(f">> Python Vision: Baixando modelo {os.path.basename(destino)}...")
        try:
            import requests
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(destino, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
        except ImportError:
            pass

def extrair_frames(video_path, ref_img_path, output_dir, min_interval=1.0):
    if not os.path.exists(video_path):
        print(f"Video nao encontrado: {video_path}")
        return 0
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Configura modelos (Mesma logica do detect_faces.py)
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    if not os.path.exists(model_dir): os.makedirs(model_dir)
    
    face_det_model = os.path.join(model_dir, "face_detection_yunet_2023mar.onnx")
    face_rec_model = os.path.join(model_dir, "face_recognition_sface_2021dec.onnx")
    
    url_det = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    url_rec = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
    
    baixar_modelo_se_necessario(url_det, face_det_model)
    baixar_modelo_se_necessario(url_rec, face_rec_model)
    
    detector = cv2.FaceDetectorYN.create(face_det_model, "", (320, 320), 0.6, 0.3, 5000)
    recognizer = cv2.FaceRecognizerSF.create(face_rec_model, "")

    # 1. Processa Referencia
    ref_img = cv2.imread(ref_img_path)
    if ref_img is None: return 0
    
    h, w, _ = ref_img.shape
    detector.setInputSize((w, h))
    _, faces = detector.detect(ref_img)
    if faces is None:
        print("Rosto nao detectado na referencia.")
        return 0
        
    face_align = recognizer.alignCrop(ref_img, faces[0])
    ref_feat = recognizer.feature(face_align)

    # 2. Processa Video
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f">> Python Vision: Extraindo fotos de {video_path}...")
    
    frame_count = 0
    saved_count = 0
    last_saved_time = -min_interval # Garante que o primeiro frame possa ser salvo
    
    # Pula frames para performance (analisa a cada 5 frames)
    skip_frames = 5 
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        current_time = frame_count / fps
        
        # Otimizacao: So processa se ja passou tempo suficiente desde a ultima foto
        if (current_time - last_saved_time) >= min_interval:
            if frame_count % skip_frames == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                sh, sw, _ = small_frame.shape
                detector.setInputSize((sw, sh))
                _, faces = detector.detect(small_frame)
                
                match_found = False
                if faces is not None:
                    for face in faces:
                        face_align = recognizer.alignCrop(small_frame, face)
                        feat = recognizer.feature(face_align)
                        score = recognizer.match(ref_feat, feat, cv2.FaceRecognizerSF_FR_COSINE)
                        
                        if score >= 0.363: # Limiar SFace
                            match_found = True
                            break
                
                if match_found:
                    filename = f"foto_{saved_count:03d}_{int(current_time)}s.jpg"
                    cv2.imwrite(os.path.join(output_dir, filename), frame)
                    print(f"   [FOTO] Salva: {filename} (Score: {score:.3f})")
                    saved_count += 1
                    last_saved_time = current_time
        
        frame_count += 1
        
    cap.release()
    print(f">> Python Vision: {saved_count} fotos extraidas.")
    return saved_count

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python extract_frames.py <video> <ref_img> <output_dir> [min_interval]")
    else:
        min_interval = 1.0
        if len(sys.argv) > 4:
            min_interval = float(sys.argv[4])
        extrair_frames(sys.argv[1], sys.argv[2], sys.argv[3], min_interval)
