"""
Módulo para gravação automática de áudio em background
"""

import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import database as db


class GravadorAudio:
    """Classe para gerenciar a gravação automática de áudio"""

    # Instância única (singleton)
    _instancia = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self):
        # Evitar reinicialização
        if hasattr(self, 'initialized'):
            return

        self.initialized = True
        self.gravando = False
        self.id_missao = None
        self.thread_gravacao = None
        self.parar_flag = False
        self.diretorio_audios = "audios_missoes"

        # Configurações de áudio
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # Mono (compatível com a maioria dos microfones)
        self.RATE = 44100  # Taxa de amostragem padrão (CD quality)

        # Criar diretório de áudios se não existir
        if not os.path.exists(self.diretorio_audios):
            os.makedirs(self.diretorio_audios)

    def iniciar_gravacao(self, id_missao, identificador_missao):
        """Inicia a gravação automática de áudio para uma missão"""
        if self.gravando:
            print(f"[ÁUDIO AVISO] Já existe uma gravação de áudio em andamento!")
            return False

        self.id_missao = id_missao
        self.identificador_missao = identificador_missao
        self.parar_flag = False
        self.gravando = True

        # Iniciar thread de gravação
        self.thread_gravacao = threading.Thread(
            target=self._gravar_em_segmentos,
            daemon=True
        )
        self.thread_gravacao.start()

        print(f"[ÁUDIO] Gravação iniciada para missão ID: {id_missao} ({identificador_missao})")
        return True

    def parar_gravacao(self):
        """Para a gravação de áudio em andamento"""
        if not self.gravando:
            print(f"[ÁUDIO AVISO] Não há gravação de áudio em andamento!")
            return False

        print(f"[ÁUDIO] Parando gravação da missão ID: {self.id_missao}...")
        self.parar_flag = True
        self.gravando = False

        # Aguardar thread finalizar (timeout de 10 segundos)
        if self.thread_gravacao and self.thread_gravacao.is_alive():
            self.thread_gravacao.join(timeout=10)

        self.id_missao = None
        self.identificador_missao = None
        print(f"[ÁUDIO] Gravação parada com sucesso!")
        return True

    def _gravar_em_segmentos(self):
        """Função principal que grava áudio em segmentos de 5 minutos"""
        DURACAO_SEGMENTO = 5 * 60  # 5 minutos em segundos

        try:
            # Inicializar PyAudio
            audio = pyaudio.PyAudio()

            # Abrir stream de áudio
            try:
                stream = audio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK
                )
            except Exception as e:
                print(f"[ÁUDIO ERRO] Não foi possível abrir o dispositivo de áudio: {e}")
                self.gravando = False
                audio.terminate()
                return

            print(f"[ÁUDIO] Dispositivo de áudio configurado: {self.RATE}Hz, {self.CHANNELS} canais")

            segmento_numero = 1

            while not self.parar_flag:
                # Criar nome do arquivo para este segmento
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"{self.identificador_missao}_seg{segmento_numero:03d}_{timestamp}.wav"
                # Usar caminho absoluto
                caminho_completo = os.path.abspath(os.path.join(self.diretorio_audios, nome_arquivo))

                print(f"[ÁUDIO] Iniciando segmento {segmento_numero}: {nome_arquivo}")
                print(f"[ÁUDIO DEBUG] Caminho completo (absoluto): {caminho_completo}")

                # Configurar arquivo WAV
                wf = wave.open(caminho_completo, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)

                tempo_inicio_segmento = time.time()
                frames_gravados = 0

                # Gravar por 5 minutos ou até receber sinal de parada
                while not self.parar_flag:
                    tempo_decorrido = time.time() - tempo_inicio_segmento

                    # Se passou 5 minutos, fechar este segmento
                    if tempo_decorrido >= DURACAO_SEGMENTO:
                        break

                    try:
                        # Ler dados do microfone
                        data = stream.read(self.CHUNK, exception_on_overflow=False)
                        wf.writeframes(data)
                        frames_gravados += 1
                    except Exception as e:
                        print(f"[ÁUDIO ERRO] Falha ao capturar áudio: {e}")
                        break

                # Fechar o arquivo de áudio deste segmento
                wf.close()

                print(f"[ÁUDIO] Segmento {segmento_numero} finalizado: {frames_gravados} frames gravados")

                # Salvar caminho no banco de dados apenas se houver frames gravados
                if frames_gravados > 0:
                    try:
                        # Aguardar um pouco para garantir que o arquivo foi escrito no disco
                        time.sleep(0.5)

                        # Verificar se o arquivo realmente existe
                        print(f"[ÁUDIO DEBUG] Verificando existência do arquivo: {caminho_completo}")
                        print(f"[ÁUDIO DEBUG] Arquivo existe? {os.path.exists(caminho_completo)}")

                        if os.path.exists(caminho_completo):
                            print(f"[ÁUDIO DEBUG] Salvando no banco o caminho: {caminho_completo}")
                            db.inserir_audio(self.id_missao, caminho_completo)
                            print(f"[ÁUDIO BANCO] Áudio salvo no banco: {caminho_completo}")
                        else:
                            print(f"[ÁUDIO ERRO] Arquivo de áudio não foi criado: {caminho_completo}")
                    except Exception as e:
                        print(f"[ÁUDIO ERRO] Falha ao salvar áudio no banco: {e}")
                else:
                    # Se não houver frames, deletar o arquivo vazio
                    if os.path.exists(caminho_completo):
                        try:
                            os.remove(caminho_completo)
                            print(f"[ÁUDIO] Arquivo vazio removido: {caminho_completo}")
                        except Exception as e:
                            print(f"[ÁUDIO ERRO] Falha ao remover arquivo vazio: {e}")

                # Se foi sinalizado para parar, sair do loop principal
                if self.parar_flag:
                    break

                # Próximo segmento
                segmento_numero += 1

            # Fechar stream e PyAudio
            stream.stop_stream()
            stream.close()
            audio.terminate()

            print(f"[ÁUDIO] Dispositivo de áudio liberado. Total de segmentos: {segmento_numero - 1}")

        except Exception as e:
            print(f"[ÁUDIO ERRO] Erro durante gravação: {e}")
            self.gravando = False

    def esta_gravando(self):
        """Verifica se há gravação de áudio em andamento"""
        return self.gravando

    def get_info_gravacao(self):
        """Retorna informações sobre a gravação de áudio atual"""
        if self.gravando:
            return {
                'gravando': True,
                'id_missao': self.id_missao,
                'identificador': self.identificador_missao
            }
        else:
            return {'gravando': False}


# Função de conveniência para obter a instância única
def get_gravador():
    """Retorna a instância única do gravador de áudio"""
    return GravadorAudio()
