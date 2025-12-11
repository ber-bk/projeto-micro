"""
Teste do microfone e gravação de áudio
"""

import pyaudio
import wave
import os

print("=== TESTE DE MICROFONE ===\n")

# Configurações
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono
RATE = 44100
RECORD_SECONDS = 3
OUTPUT_FILE = "teste_audio.wav"

print("1. Inicializando PyAudio...")
audio = pyaudio.PyAudio()

# Listar dispositivos de áudio
print("\n2. Dispositivos de áudio disponíveis:")
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f"   [{i}] {info['name']}")
    print(f"       - Canais de entrada: {info['maxInputChannels']}")
    print(f"       - Canais de saída: {info['maxOutputChannels']}")

print(f"\n3. Tentando abrir microfone...")
try:
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    print("   [OK] Microfone aberto com sucesso!")
except Exception as e:
    print(f"   [ERRO] Falha ao abrir microfone: {e}")
    audio.terminate()
    exit(1)

print(f"\n4. Gravando {RECORD_SECONDS} segundos de áudio...")
print("   FALE ALGUMA COISA NO MICROFONE!")

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)
    if i % 10 == 0:
        print("   .", end="", flush=True)

print("\n   [OK] Gravação concluída!")

print("\n5. Fechando stream...")
stream.stop_stream()
stream.close()
audio.terminate()
print("   [OK] Stream fechado!")

print(f"\n6. Salvando arquivo {OUTPUT_FILE}...")
wf = wave.open(OUTPUT_FILE, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

if os.path.exists(OUTPUT_FILE):
    tamanho = os.path.getsize(OUTPUT_FILE)
    print(f"   [OK] Arquivo criado com sucesso!")
    print(f"   - Tamanho: {tamanho} bytes ({tamanho / 1024:.2f} KB)")
else:
    print(f"   [ERRO] Arquivo não foi criado!")

print("\n=== TESTE CONCLUÍDO ===")
print(f"Reproduza o arquivo '{OUTPUT_FILE}' para verificar se o áudio foi gravado corretamente.")
