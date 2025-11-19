from telemetry.telemetry_recorder import TelemetryRecorder

def main():
    """
    Fluxo principal da gravação completa (vídeo + áudio).
    """

    recorder = TelemetryRecorder(camera_index=0)

    # Inicia vídeo + áudio
    if not recorder.start_all():
        return

    # Loop unificado
    recorder.run()

if __name__ == "__main__":
    main()
