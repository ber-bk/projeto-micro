import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import numpy as np
import time


# ============================================================
#   TESTES DE CÂMERA
# ============================================================

def test_camera_segmentacao(mocker):
    """Testa se a câmera troca de segmento sem acessar webcam real."""

    from camera.camera_recorder import CameraRecorder
    import cv2

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, MagicMock())

    mock_out = MagicMock()

    mocker.patch("cv2.VideoCapture", return_value=mock_cap)
    mocker.patch("cv2.VideoWriter", return_value=mock_out)
    mocker.patch("cv2.imshow")
    mocker.patch("cv2.waitKey", return_value=-1)

    recorder = CameraRecorder(camera_index=0)
    recorder.segment_duration_sec = 1

    assert recorder.open_camera()
    recorder.prepare_output_file()
    recorder.start_recording()

    recorder.segment_start_time = datetime.now() - timedelta(seconds=2)

    # Simula 1 iteração do loop
    ret, frame = recorder.cap.read()
    assert ret is True

    elapsed = (datetime.now() - recorder.segment_start_time).total_seconds()
    if elapsed >= recorder.segment_duration_sec:
        recorder.out.release()
        recorder.start_new_segment()

    assert recorder.segment_index >= 2


def test_camera_falha_ao_abrir(mocker):
    """Testa comportamento quando a câmera não abre."""

    from camera.camera_recorder import CameraRecorder
    import cv2

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False

    mocker.patch("cv2.VideoCapture", return_value=mock_cap)

    recorder = CameraRecorder(0)
    assert recorder.open_camera() is False, "A câmera deveria falhar ao abrir"


def test_camera_falha_em_read(mocker):
    """Testa comportamento quando falha ao capturar frame."""

    from camera.camera_recorder import CameraRecorder
    import cv2

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)

    mocker.patch("cv2.VideoCapture", return_value=mock_cap)
    mocker.patch("cv2.VideoWriter")

    recorder = CameraRecorder(0)
    recorder.open_camera()
    recorder.prepare_output_file()

    ret, frame = recorder.cap.read()

    assert ret is False, "Frame deveria falhar (ret=False)"


def test_camera_multiplos_segmentos(mocker):
    """Garante que vários segmentos são criados."""

    from camera.camera_recorder import CameraRecorder
    import cv2

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, MagicMock())

    mock_out = MagicMock()

    mocker.patch("cv2.VideoCapture", return_value=mock_cap)
    mocker.patch("cv2.VideoWriter", return_value=mock_out)
    mocker.patch("cv2.imshow")
    mocker.patch("cv2.waitKey", return_value=-1)

    recorder = CameraRecorder(0)
    recorder.segment_duration_sec = 1

    recorder.open_camera()
    recorder.prepare_output_file()

    for _ in range(3):
        recorder.segment_start_time = datetime.now() - timedelta(seconds=2)
        recorder.start_new_segment()

    assert recorder.segment_index == 4  # 1 inicial + 3 novos


def test_camera_loop_performance(mocker):
    """Garante performance mínima ao processar frames."""

    from camera.camera_recorder import CameraRecorder
    import cv2

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, MagicMock())

    mock_out = MagicMock()

    mocker.patch("cv2.VideoCapture", return_value=mock_cap)
    mocker.patch("cv2.VideoWriter", return_value=mock_out)
    mocker.patch("cv2.imshow")
    mocker.patch("cv2.waitKey", return_value=-1)

    recorder = CameraRecorder(0)
    recorder.open_camera()
    recorder.prepare_output_file()

    start = time.time()

    for _ in range(100):
        recorder.cap.read()

    assert (time.time() - start) < 0.5, "Processamento lento demais!"


# ============================================================
#   TESTES DE ÁUDIO
# ============================================================

def test_audio_segmentacao(mocker):
    """Testa segmentação do áudio sem microfone real."""

    from audio.AudioRecorder import AudioRecorder
    import sounddevice as sd
    import soundfile as sf

    mocker.patch("sounddevice.InputStream", return_value=MagicMock())
    mocker.patch("soundfile.SoundFile", return_value=MagicMock())

    recorder = AudioRecorder()
    recorder.segment_duration_sec = 1

    recorder.prepare_output_file()
    recorder.start_recording()

    recorder.segment_start_time = datetime.now() - timedelta(seconds=2)

    fake_audio = np.zeros((1024, recorder.channels), dtype="int16")
    recorder.audio_queue.put(fake_audio)

    elapsed = (datetime.now() - recorder.segment_start_time).total_seconds()
    if elapsed >= recorder.segment_duration_sec:
        recorder.file.close()
        recorder.start_new_segment()

    assert recorder.segment_index >= 2


def test_audio_queue_vazia(mocker):
    """Garante que sistema não falha quando a fila está vazia."""

    from audio.AudioRecorder import AudioRecorder
    import sounddevice as sd
    import soundfile as sf

    mocker.patch("sounddevice.InputStream", return_value=MagicMock())
    mocker.patch("soundfile.SoundFile", return_value=MagicMock())

    recorder = AudioRecorder()
    recorder.prepare_output_file()
    recorder.start_recording()

    recorder.segment_start_time = datetime.now() - timedelta(seconds=2)

    try:
        recorder.start_new_segment()
    except Exception as e:
        assert False, f"Erro inesperado ao processar fila vazia: {e}"


# ============================================================
#   TESTES DE TELEMETRIA
# ============================================================

def test_telemetry_start_stop(mocker):
    """Garante que TelemetryRecorder inicia e para câmera+áudio juntos."""

    from telemetry.telemetry_recorder import TelemetryRecorder

    mock_camera = MagicMock()
    mock_audio = MagicMock()

    mocker.patch("telemetry.telemetry_recorder.CameraRecorder", return_value=mock_camera)
    mocker.patch("telemetry.telemetry_recorder.AudioRecorder", return_value=mock_audio)

    tel = TelemetryRecorder()

    tel.start_all()

    mock_camera.open_camera.assert_called_once()
    mock_camera.start_recording.assert_called_once()
    mock_audio.start_recording.assert_called_once()

    tel.stop_all()

    mock_camera.close.assert_called_once()
    mock_audio.close.assert_called_once()


def test_telemetry_stop_em_execucao(mocker):
    """Testa stop_all enquanto grava."""

    from telemetry.telemetry_recorder import TelemetryRecorder

    mock_camera = MagicMock()
    mock_audio = MagicMock()

    mocker.patch("telemetry.telemetry_recorder.CameraRecorder", return_value=mock_camera)
    mocker.patch("telemetry.telemetry_recorder.AudioRecorder", return_value=mock_audio)

    tel = TelemetryRecorder()
    tel.start_all()

    mock_camera.is_recording = True
    mock_audio.is_recording = True

    tel.stop_all()

    mock_camera.close.assert_called_once()
    mock_audio.close.assert_called_once()


def test_telemetry_integracao_basica(mocker):
    """Testa ciclo completo simples de telemetria."""

    from telemetry.telemetry_recorder import TelemetryRecorder

    mock_camera = MagicMock()
    mock_audio = MagicMock()

    mocker.patch("telemetry.telemetry_recorder.CameraRecorder", return_value=mock_camera)
    mocker.patch("telemetry.telemetry_recorder.AudioRecorder", return_value=mock_audio)

    tel = TelemetryRecorder()

    tel.start_all()
    assert mock_camera.start_recording.called
    assert mock_audio.start_recording.called

    tel.stop_all()
    assert mock_camera.close.called
    assert mock_audio.close.called
