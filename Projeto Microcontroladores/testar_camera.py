"""
Script de teste para verificar se a câmera e gravação estão funcionando
"""

import cv2
import os

print("=== TESTE DE CÂMERA E GRAVAÇÃO ===\n")

# 1. Verificar se OpenCV está instalado
print("1. Testando OpenCV...")
print(f"   Versão do OpenCV: {cv2.__version__}")

# 2. Testar abertura da câmera
print("\n2. Testando abertura da câmera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("   [ERRO] Nao foi possivel abrir a camera!")
    exit(1)
else:
    print("   [OK] Camera aberta com sucesso!")

# 3. Obter configurações da câmera
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20
largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"\n3. Configurações da câmera:")
print(f"   - FPS: {fps}")
print(f"   - Resolução: {largura}x{altura}")

# 4. Capturar um frame de teste
print("\n4. Testando captura de frame...")
ret, frame = cap.read()

if not ret:
    print("   [ERRO] Nao foi possivel capturar frame!")
    cap.release()
    exit(1)
else:
    print(f"   [OK] Frame capturado com sucesso! Tamanho: {frame.shape}")

# 5. Criar pasta de teste
print("\n5. Criando pasta de teste...")
pasta_teste = "teste_videos"
if not os.path.exists(pasta_teste):
    os.makedirs(pasta_teste)
print(f"   [OK] Pasta criada: {pasta_teste}")

# 6. Testar gravação de vídeo
print("\n6. Testando gravação de vídeo...")
caminho_teste = os.path.abspath(os.path.join(pasta_teste, "teste.avi"))
print(f"   Caminho do arquivo: {caminho_teste}")

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(caminho_teste, fourcc, fps, (largura, altura))

print("   Gravando 60 frames...")
for i in range(60):
    ret, frame = cap.read()
    if ret:
        out.write(frame)

out.release()
cap.release()

# 7. Verificar se arquivo foi criado
print("\n7. Verificando se arquivo foi criado...")
if os.path.exists(caminho_teste):
    tamanho = os.path.getsize(caminho_teste)
    print(f"   [OK] Arquivo criado com sucesso!")
    print(f"   - Caminho: {caminho_teste}")
    print(f"   - Tamanho: {tamanho} bytes ({tamanho / 1024:.2f} KB)")
else:
    print(f"   [ERRO] Arquivo nao foi criado!")

print("\n=== FIM DO TESTE ===")
