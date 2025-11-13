import cv2
from datetime import datetime
from pathlib import Path


def main():
    """
    Função principal que controla o fluxo da captura e gravação do vídeo.

    Etapas:
    1. Abrir a câmera USB ou interna do laptop.
    2. Configurar parâmetros como codec (MJPG), resolução e FPS.
    3. Criar automaticamente a pasta de saída para salvar vídeos.
    4. Gravar cada frame capturado em um arquivo .avi.
    5. Exibir o vídeo em tempo real na tela.
    6. Liberar todos os recursos ao final.

    A tecla 'q' encerra o processo.
    """

    # Abrir a câmera USB
    # 0 para webcam interna do Laptop
    # 1 para câmera USB externa
    cap = cv2.VideoCapture(1)

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
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    # Verifica se a câmera abriu corretamente
    """ cap.isOpened() retorna True apenas se a câmera conseguiu ser inicializada corretamente.
        Caso o índice da câmera esteja errado (0/1/2) ou o cabo esteja desconectado, retorna False.
    """
    if not cap.isOpened():
        print("Erro: não consegui abrir a câmera. Verifique o cabo USB e o índice da câmera.")
        return

    # Verificar a resolução real da câmera
    """ CAP_PROP_FRAME_WIDTH e CAP_PROP_FRAME_HEIGHT retornam o tamanho real dos frames capturados.
        Algumas câmeras retornam 0 antes de transmitir o primeiro frame, por isso usamos "or 640/480" como fallback.
    """
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    print("Resolução detectada:", frame_width, "x", frame_height)

    # FPS - câmeras industriais quase sempre retornam 0 → forçamos 30
    """ CAP_PROP_FPS normalmente retorna a taxa nativa de frames por segundo.
        Porém, muitas câmeras USB baratas/industriais não reportam esse valor corretamente, retornando 0.
        Por isso definimos um valor padrão de 30 FPS quando não há informação disponível.
    """
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS detectado:", fps)
    if fps == 0 or fps is None:
        fps = 30.0
    print("FPS detectado/forçado:", fps)

    # Pasta onde os vídeos serão salvos
    """ Aqui salvamos o vídeo na pasta 'videos'.
        __file__ é o caminho do arquivo atual. Usamos resolve() para obter o caminho absoluto, 
        parent.parent para subir dois níveis (até a raiz do projeto) e então adicionamos "videos" usando / "videos".
        
        Isso torna o projeto portátil e independente do local onde o script foi executado,
        garantindo que todos os vídeos fiquem sempre organizados dentro da pasta do projeto.
    """
    videos_dir = Path(__file__).resolve().parent.parent / "videos"
    videos_dir.mkdir(exist_ok=True)

    # Nome do arquivo baseado na data/hora
    """ Criamos nomes únicos para os arquivos usando timestamp.
        datetime.now() obtém a data e hora atual.
        strftime() formata essa data em texto, no formato: AAAA-MM-DD_HH-MM-SS.
        Isso evita sobrescrever arquivos e organiza bem os registros de mergulho.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = videos_dir / f"mergulho_{timestamp}.avi"

    # Configura o writer com MJPG
    """" Configuramos o VideoWriter para salvar o vídeo com o codec MJPG, que é amplamente suportado e oferece boa qualidade.
         O arquivo será salvo com o nome gerado anteriormente, na resolução e FPS detectados/forçados.
         out é o objeto que escreverá os frames no arquivo de vídeo. Ele possui o método write() que será usado para salvar cada frame capturado.

         Parâmetros:
         - str(video_filename): caminho completo do arquivo de saída
         - fourcc: codec de compressão (MJPG)
         - fps: taxa de frames por segundo do vídeo
         - (frame_width, frame_height): resolução do vídeo

         O arquivo .avi gerado é apenas um *container*, e o MJPG é o codec interno usado para comprimir os frames.
    """
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(
        str(video_filename),
        fourcc,
        fps,
        (frame_width, frame_height)
    )

    # Verifica se o arquivo foi aberto corretamente
    """ out.isOpened() retorna False quando o OpenCV não consegue criar o arquivo .avi,
        frequentemente por falta de permissões de escrita, caminhos inválidos ou codecs não suportados.
    """
    if not out.isOpened():
        print("Erro: não consegui criar o arquivo de vídeo.")
        cap.release()
        return

    print(f"Gravando vídeo em: {video_filename}")
    print("Pressione 'q' na janela de vídeo para parar a gravação.")

    # Loop principal: ler da câmera, mostrar e gravar
    """ Este loop roda até o usuário apertar 'q'.
        Em cada iteração:
        - cap.read() captura um frame da câmera.
        - out.write(frame) adiciona esse frame ao arquivo .avi.
        - cv2.imshow exibe o frame na tela para visualização em tempo real.
        - cv2.waitKey(1) verifica se alguma tecla foi pressionada.
    """
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Falha ao ler frame da câmera. Encerrando.")
            break

        # Escreve o frame no arquivo de saída
        out.write(frame)

        # Mostra o frame na tela
        cv2.imshow("Capacete - Camera (press 'q' para sair)", frame)

        # Espera 1 ms por tecla. Se for 'q', sai.
        """ waitKey(1) retorna o código da tecla pressionada.
            Usamos & 0xFF, que é uma máscara bit a bit, para garantir compatibilidade entre sistemas.
            Se a tecla for 'q', interrompemos o loop.
        """
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Libera recursos
    """ É fundamental liberar recursos ao final.
        - cap.release(): desativa a câmera.
        - out.release(): finaliza e salva o arquivo .avi.
        - cv2.destroyAllWindows(): fecha todas as janelas abertas pelo OpenCV.
    """
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Gravação finalizada.")


if __name__ == "__main__":
    main()
