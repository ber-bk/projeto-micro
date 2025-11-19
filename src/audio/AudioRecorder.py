import sounddevice as sd
import soundfile as sf
from datetime import datetime
from pathlib import Path
import queue


class AudioRecorder:
    """
    Classe responsável por capturar e gravar áudio do microfone.
    Este módulo segue a mesma filosofia do CameraRecorder, mas aqui
    o áudio é mantido em captura contínua, sem interrupções, para evitar
    falhas de sincronização entre segmentos.
    """

    def __init__(self, samplerate=44100, channels=1):
        """
        Inicializa variáveis internas do gravador de áudio.

        """
        self.samplerate = samplerate
        self.channels = channels

        self.audio_queue = queue.Queue()     # Buffer que armazena os blocos de áudio
        self.stream = None                   # Stream contínuo do microfone
        self.file = None                     # Arquivo WAV em escrita
        self.audio_filename = None           # Nome do arquivo atual

        self.segment_duration_sec = 5 * 60   # 5 minutos por segmento
        self.segment_start_time = None
        self.segment_index = 1

    def _audio_callback(self, indata, frames, time, status):
        """
        Callback do sounddevice. É chamado automaticamente sempre que
        novos bytes de áudio chegam do microfone.

        Não escrevemos no arquivo aqui, pois isso travaria o callback;
        apenas colocamos o áudio na fila (queue) para o loop principal salvar.
        """
        if status:
            print("Status do áudio:", status)
        self.audio_queue.put(indata.copy())

    def prepare_output_file(self):
        """
        Cria a pasta de gravações de áudio e gera o nome do arquivo WAV.
        """

        """ Segue mesma filosofia do vídeo:
            - pasta fixa dentro do projeto (audio/gravacoes)
            - nomes baseados em timestamp
        """
        base_dir = Path(__file__).resolve().parents[1] / "audio" / "gravacoes"
        base_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.audio_filename = base_dir / f"audio_{timestamp}.wav"

    def start_new_segment(self):
        """
        Inicia um novo arquivo WAV de segmento.
        O stream de áudio continua aberto — apenas trocamos os arquivos.
        """

        base_dir = Path(__file__).resolve().parents[1] / "audio" / "gravacoes"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.audio_filename = base_dir / f"audio_{timestamp}_parte{self.segment_index}.wav"

        """ soundfile abre o arquivo WAV em modo de escrita.
            - samplerate define a taxa de amostragem
            - channels define quantos canais (mono ou stereo)
            - subtype="PCM_16" garante compatibilidade máxima
        """
        self.file = sf.SoundFile(
            self.audio_filename,
            mode='w',
            samplerate=self.samplerate,
            channels=self.channels,
            subtype='PCM_16'
        )

        self.segment_start_time = datetime.now()
        print(f"[AUDIO - SEGMENTO] Gravando arquivo:", self.audio_filename)

        self.segment_index += 1

    def start_recording(self):
        """
        Inicia o stream contínuo de captura de áudio e cria o primeiro segmento.
        """

        self.start_new_segment()

        """ sounddevice.InputStream abre o microfone e chama o callback
            automaticamente sempre que há dados.
        """
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self._audio_callback
        )

        self.stream.start()
        print("Captura de áudio iniciada.")

        return True

    def record_loop(self):
        """
        Loop principal que:
        - lê blocos de áudio da fila
        - salva no arquivo WAV
        - cria novos segmentos a cada X minutos
        """

        print("Gravando áudio... pressione CTRL+C para parar.")

        try:
            while True:

                # Pega próximo bloco de áudio enviado pelo callback
                block = self.audio_queue.get()

                # Tempo decorrido do segmento atual
                elapsed = (datetime.now() - self.segment_start_time).total_seconds()

                # Ao atingir o tempo limite → troca de arquivo
                if elapsed >= self.segment_duration_sec:
                    print("[AUDIO - SEGMENTO] Criando novo arquivo...")
                    self.file.close()
                    self.start_new_segment()

                # Salva o bloco no arquivo atual
                self.file.write(block)

        except KeyboardInterrupt:
            print("\nInterrupção solicitada pelo usuário.")

        finally:
            self.close()

    def close(self):
        """
        Libera recursos: fecha stream, arquivo e esvazia filas.
        """

        """ Assim como no vídeo:
            - stream.stop() e stream.close() desligam o microfone
            - file.close() salva e fecha o WAV
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()

        if self.file:
            self.file.close()

        print("Gravação de áudio finalizada.")
