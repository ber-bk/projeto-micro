import cv2
from datetime import datetime
from pathlib import Path




class CameraRecorder:
    """
    Classe responsável por capturar e gravar vídeo da câmera USB.
    Este código foi extraído e reorganizado a partir do script original
    para modularizar a lógica e facilitar futuras integrações com dashboard
    e telemetria.
    """

    def __init__(self, camera_index=1):
        """
        Inicializa variáveis internas e define o índice da câmera.

        """
        self.camera_index = camera_index
        self.cap = None
        self.out = None
        self.video_filename = None
        self.fps = None
        self.frame_width = None
        self.frame_height = None

        self.segment_duration_sec = 5*60     # 5 minutos
        self.segment_start_time = None
        self.segment_index = 1

    def open_camera(self):
        """
        Abre a câmera e aplica configurações iniciais como codec MJPG,
        resolução e FPS.

        (Docstrings e comentários abaixo são do código original)
        """
        self.cap = cv2.VideoCapture(self.camera_index)

        # Forçar MJPG para melhor compatibilidade com várias câmeras
        """ set muda uma propriedade da captura de vídeo. 
            CAP_PROP_FOURCC define o codec de vídeo. FOUCC é um código de quatro caracteres que especifica o codec usado para comprimir os vídeos. 
            VideoWriter_fourcc é uma função que converte esses quatro caracteres em um valor numérico que o OpenCV pode usar.
            Aqui estamos configurando para usar o codec MJPG (Motion JPEG), 
            que é amplamente suportado por muitas câmeras USB e oferece um bom equilíbrio entre qualidade e compressão.

            IMPORTANTE:
            Muitas câmeras USB industriais enviam vídeo nativamente em MJPEG. 
            Forçar esse formato evita lag, reduz consumo de CPU, aumenta a taxa de FPS e melhora a compatibilidade geral.
        """
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        # Verifica se a câmera abriu corretamente
        """ cap.isOpened() retorna True apenas se a câmera conseguiu ser inicializada corretamente.
            Caso o índice da câmera esteja errado (0/1/2) ou o cabo esteja desconectado, retorna False.
        """
        if not self.cap.isOpened():
            print("Erro: não consegui abrir a câmera. Verifique o cabo USB e o índice da câmera.")
            return False

        # Verificar a resolução real da câmera
        """ CAP_PROP_FRAME_WIDTH e CAP_PROP_FRAME_HEIGHT retornam o tamanho real dos frames capturados.
            Algumas câmeras retornam 0 antes de transmitir o primeiro frame, por isso usamos "or 640/480" como fallback.
        """
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        print("Resolução detectada:", self.frame_width, "x", self.frame_height)

        # FPS - câmeras industriais quase sempre retornam 0 → forçamos 30
        """ CAP_PROP_FPS normalmente retorna a taxa nativa de frames por segundo.
            Porém, muitas câmeras USB baratas/industriais não reportam esse valor corretamente, retornando 0.
            Por isso definimos um valor padrão de 30 FPS quando não há informação disponível.
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        print("FPS detectado:", fps)
        self.fps = fps if fps not in (0, None) else 30.0
        print("FPS detectado/forçado:", self.fps)

        return True

    def prepare_output_file(self):
        """
        Gera o nome do arquivo .avi baseado em timestamp e cria a pasta
        'gravacoes/video' na raiz do projeto.
        """

        from pathlib import Path
        from datetime import datetime

        # Caminho: <projeto>/gravacoes/video
        videos_dir = (
            Path(__file__).resolve().parents[2]
            / "gravacoes"
            / "video"
        )
        videos_dir.mkdir(parents=True, exist_ok=True)

        # Nome baseado no timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.video_filename = videos_dir / f"mergulho_{timestamp}.avi"


    def start_new_segment(self):
        """
        Cria um novo arquivo de vídeo para iniciar um novo segmento.
        Mantém FPS, resolução e codec, mas troca o nome do arquivo.
        """

        # <<< CORRIGIDO: antes estava apontando para /videos >>>
        videos_dir = (
            Path(__file__).resolve().parents[2]
            / "gravacoes"
            / "video"
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = f"mergulho_{timestamp}_parte{self.segment_index}.avi"
        self.video_filename = videos_dir / base_name

        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        self.out = cv2.VideoWriter(
            str(self.video_filename),
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )

        self.segment_start_time = datetime.now()
        print(f"[SEGMENTO] Gravando arquivo: {self.video_filename}")
        self.segment_index += 1

    def start_recording(self):
        """
        Inicializa o objeto VideoWriter responsável por salvar frames no arquivo .avi.
        """

        # Apenas inicializa a primeira vez (segmento 1)
        self.start_new_segment()
        return True

    def record_loop(self):
        """
        Loop principal de leitura dos frames, exibição e gravação.
        Todos os comentários foram mantidos do script original.
        """

        while True:
            ret, frame = self.cap.read()

            if not ret:
                print("Falha ao ler frame da câmera. Encerrando.")
                break

            elapsed = (datetime.now() - self.segment_start_time).total_seconds()
            if elapsed >= self.segment_duration_sec:
                print("[SEGMENTO] Criando novo arquivo de vídeo...")
                self.out.release()
                self.start_new_segment()

            self.out.write(frame)

            cv2.imshow("Capacete - Camera (press 'q' para sair)", frame)
            key = cv2.waitKey(1)
            if key != -1 and chr(key).lower() == "q":
                break

        self.close()

    def close(self):
        """
        Libera recursos: câmera, arquivo e janelas.
        """
        if self.cap:
            self.cap.release()

        if self.out:
            self.out.release()

        cv2.destroyAllWindows()

        print("Gravação finalizada.")
