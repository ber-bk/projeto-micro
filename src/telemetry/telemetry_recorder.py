from camera.camera_recorder import CameraRecorder
from audio.AudioRecorder import AudioRecorder

class TelemetryRecorder:
    """
    Classe responsável por coordenar a gravação simultânea de:
    - Vídeo (CameraRecorder)
    - Áudio (AudioRecorder)

    Esta classe funciona como um orquestrador: ela inicia todos os módulos,
    para todos, e fornece uma interface única para o sistema de telemetria.
    """

    def __init__(self, camera_index=0):
        """
        Inicializa os gravadores de vídeo e áudio.

        """
        self.camera = CameraRecorder(camera_index=camera_index)
        self.audio = AudioRecorder()

        self.running = False

    def start_all(self):
        """
        Inicia vídeo e áudio de forma segura.
        """

        # Abre e configura a câmera
        if not self.camera.open_camera():
            print("Erro ao abrir a câmera. Abortando.")
            return False

        self.camera.prepare_output_file()

        if not self.camera.start_recording():
            print("Erro ao iniciar a gravação de vídeo. Abortando.")
            return False

        # Inicia o gravador de áudio
        if not self.audio.start_recording():
            print("Erro ao iniciar a gravação de áudio. Abortando.")
            return False

        self.running = True
        print("✓ Telemetria iniciada (vídeo + áudio)")
        return True

    def run(self):
        """
        Executa o loop principal de gravação:
        - vídeo controla o loop (tecla 'q')
        - áudio é salvo continuamente em paralelo
        """

        if not self.running:
            print("Telemetria não iniciada. Chame start_all().")
            return

        print("Gravando telemetria (vídeo + áudio)...")

        try:
            # O loop do vídeo é quem controla execução (exibe janela, tecla Q etc.)
            self.camera.record_loop()

        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário.")

        finally:
            self.stop_all()

    def stop_all(self):
        """
        Para todos os módulos de telemetria.
        """

        print("\nEncerrando telemetria...")

        self.camera.close()
        self.audio.close()

        self.running = False

        print("✓ Todos os sistemas encerrados com segurança.")
