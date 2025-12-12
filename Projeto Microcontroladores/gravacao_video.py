"""
Módulo para gravação automática de vídeo em background
"""

import cv2
import threading
import time
import os
from datetime import datetime
import database as db
import sensor_arduino


class GravadorVideo:
    """Classe para gerenciar a gravação automática de vídeo"""

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
        self.diretorio_videos = "videos_missoes"

        # Frame compartilhado para visualização ao vivo
        self.ultimo_frame = None
        self.frame_lock = threading.Lock()

        # Criar diretório de vídeos se não existir
        if not os.path.exists(self.diretorio_videos):
            os.makedirs(self.diretorio_videos)

    def iniciar_gravacao(self, id_missao, identificador_missao):
        """Inicia a gravação automática para uma missão"""
        if self.gravando:
            print(f"[AVISO] Já existe uma gravação em andamento!")
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

        print(f"[GRAVAÇÃO] Iniciada para missão ID: {id_missao} ({identificador_missao})")
        return True

    def parar_gravacao(self):
        """Para a gravação em andamento"""
        if not self.gravando:
            print(f"[AVISO] Não há gravação em andamento!")
            return False

        print(f"[GRAVAÇÃO] Parando gravação da missão ID: {self.id_missao}...")
        self.parar_flag = True
        self.gravando = False

        # Aguardar thread finalizar (timeout de 10 segundos)
        if self.thread_gravacao and self.thread_gravacao.is_alive():
            self.thread_gravacao.join(timeout=10)

        self.id_missao = None
        self.identificador_missao = None
        print(f"[GRAVAÇÃO] Parada com sucesso!")
        return True

    def _gravar_em_segmentos(self):
        """Função principal que grava em segmentos de 5 minutos"""
        DURACAO_SEGMENTO = 5 * 60  # 5 minutos em segundos

        try:
            # Abrir câmera
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("[ERRO] Não foi possível abrir a câmera!")
                self.gravando = False
                return

            # Configurações da câmera
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 20  # FPS padrão se não conseguir obter
            largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            print(f"[GRAVAÇÃO] Câmera configurada: {largura}x{altura} @ {fps}fps")

            segmento_numero = 1

            while not self.parar_flag:
                # Criar nome do arquivo para este segmento
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"{self.identificador_missao}_seg{segmento_numero:03d}_{timestamp}.avi"
                # Usar caminho absoluto
                caminho_completo = os.path.abspath(os.path.join(self.diretorio_videos, nome_arquivo))

                # Configurar codec e writer
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(caminho_completo, fourcc, fps, (largura, altura))

                print(f"[GRAVAÇÃO] Iniciando segmento {segmento_numero}: {nome_arquivo}")
                print(f"[DEBUG] Caminho completo (absoluto): {caminho_completo}")

                tempo_inicio_segmento = time.time()
                frames_gravados = 0

                # Gravar por 5 minutos ou até receber sinal de parada
                while not self.parar_flag:
                    tempo_decorrido = time.time() - tempo_inicio_segmento

                    # Se passou 5 minutos, fechar este segmento
                    if tempo_decorrido >= DURACAO_SEGMENTO:
                        break

                    ret, frame = cap.read()

                    if not ret:
                        print("[ERRO] Falha ao capturar frame")
                        break

                    # Obter dados dos sensores
                    sensor = sensor_arduino.get_sensor()
                    temperatura = sensor.get_temperatura_valor()
                    pressao = sensor.get_pressao_valor()

                    # Verde claro para todos os textos
                    cor_verde_claro = (100, 255, 100)

                    # Adicionar informações no frame (mais nítidas e limpas)
                    texto_missao = f"{self.identificador_missao}"
                    texto_sensores = f"Temperatura: {temperatura}  Pressao: {pressao}"

                    # Textos maiores e mais espessos para melhor nitidez
                    cv2.putText(frame, texto_missao, (10, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_verde_claro, 2, cv2.LINE_AA)
                    cv2.putText(frame, texto_sensores, (10, 75),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_verde_claro, 2, cv2.LINE_AA)

                    # Gravar frame
                    out.write(frame)
                    frames_gravados += 1

                    # Armazenar frame para visualização ao vivo
                    with self.frame_lock:
                        self.ultimo_frame = frame.copy()

                    # Pequeno delay para não sobrecarregar o CPU
                    time.sleep(1.0 / fps)

                # Fechar o arquivo de vídeo deste segmento
                out.release()

                print(f"[GRAVAÇÃO] Segmento {segmento_numero} finalizado: {frames_gravados} frames gravados")

                # Salvar caminho no banco de dados apenas se houver frames gravados
                if frames_gravados > 0:
                    try:
                        # Aguardar um pouco para garantir que o arquivo foi escrito no disco
                        time.sleep(0.5)

                        # Verificar se o arquivo realmente existe
                        print(f"[DEBUG] Verificando existência do arquivo: {caminho_completo}")
                        print(f"[DEBUG] Arquivo existe? {os.path.exists(caminho_completo)}")

                        if os.path.exists(caminho_completo):
                            print(f"[DEBUG] Salvando no banco o caminho: {caminho_completo}")
                            db.inserir_video(self.id_missao, caminho_completo)
                            print(f"[BANCO] Vídeo salvo no banco: {caminho_completo}")
                        else:
                            print(f"[ERRO] Arquivo de vídeo não foi criado: {caminho_completo}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao salvar vídeo no banco: {e}")
                else:
                    # Se não houver frames, deletar o arquivo vazio
                    if os.path.exists(caminho_completo):
                        try:
                            os.remove(caminho_completo)
                            print(f"[GRAVAÇÃO] Arquivo vazio removido: {caminho_completo}")
                        except Exception as e:
                            print(f"[ERRO] Falha ao remover arquivo vazio: {e}")

                # Se foi sinalizado para parar, sair do loop principal
                if self.parar_flag:
                    break

                # Próximo segmento
                segmento_numero += 1

            # Liberar câmera
            cap.release()
            print(f"[GRAVAÇÃO] Câmera liberada. Total de segmentos: {segmento_numero - 1}")

        except Exception as e:
            print(f"[ERRO] Erro durante gravação: {e}")
            self.gravando = False

    def esta_gravando(self):
        """Verifica se há gravação em andamento"""
        return self.gravando

    def get_info_gravacao(self):
        """Retorna informações sobre a gravação atual"""
        if self.gravando:
            return {
                'gravando': True,
                'id_missao': self.id_missao,
                'identificador': self.identificador_missao
            }
        else:
            return {'gravando': False}

    def get_ultimo_frame(self):
        """Retorna o último frame capturado (para visualização ao vivo)"""
        with self.frame_lock:
            if self.ultimo_frame is not None:
                return self.ultimo_frame.copy()
            return None


# Função de conveniência para obter a instância única
def get_gravador():
    """Retorna a instância única do gravador"""
    return GravadorVideo()
