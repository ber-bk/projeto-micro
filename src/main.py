from camera_recorder import CameraRecorder

def main():
    """
    Função principal que coordena o uso da classe CameraRecorder.

    Etapas:
    1. Inicializa o objeto responsável pela captura e gravação.
    2. Abre a câmera e configura codec, FPS e resolução.
    3. Prepara o arquivo de saída (.avi) com timestamp.
    4. Inicia a captura e gravação dos frames.
    5. Entra no loop principal de gravação até o usuário apertar 'q'.
    """

    # Criamos o gravador de vídeo e escolhemos qual câmera usar.
    # 0 = webcam interna | 1 = câmera USB externa.
    recorder = CameraRecorder(camera_index=1)

    # Abre e configura a câmera (codec, resolução, FPS).
    if not recorder.open_camera():
        return

    # Gera o nome do arquivo e garante que a pasta "videos" exista.
    recorder.prepare_output_file()

    # Inicializa o objeto de escrita do arquivo .avi com MJPG.
    if not recorder.start_recording():
        return

    # Loop principal: lê frames, grava no arquivo e mostra na tela.
    recorder.record_loop()


if __name__ == "__main__":
    # Executa o fluxo principal do programa.
    main()
