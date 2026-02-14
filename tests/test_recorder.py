import pytest
import os
import time
from unittest.mock import MagicMock, patch
from recorder import AudioRecorder

@pytest.fixture
def mock_pyaudio(mocker):
    # Mock de PyAudio para evitar usar el micrófono real
    mock_pa = mocker.patch("recorder.pyaudio.PyAudio")
    mock_instance = mock_pa.return_value
    
    # Mock del stream
    mock_stream = MagicMock()
    mock_instance.open.return_value = mock_stream
    # Simular que leer audio devuelve bytes vacíos
    mock_stream.read.return_value = b"\x00" * 1024
    
    return mock_instance

def test_recorder_init(mock_pyaudio):
    recorder = AudioRecorder("test_audio.wav")
    assert "test_audio.wav" in recorder.filename
    assert recorder.is_recording is False

def test_start_stop_recording(mock_pyaudio, tmp_path):
    # Usar un archivo temporal para el test
    test_file = str(tmp_path / "test.wav")
    recorder = AudioRecorder(test_file)
    
    # Mock de _save_file para no escribir realmente en disco si no queremos
    # Pero aquí probaremos el flujo completo mockeando solo el hardware
    with patch.object(AudioRecorder, "_save_file") as mock_save:
        assert recorder.start_recording() is True
        assert recorder.is_recording is True
        
        time.sleep(0.1) # Dejar que el hilo de grabación corra un poco
        
        # Simulamos que se capturaron frames
        recorder.frames = [b"\x00\x01"]
        
        result_path = recorder.stop_recording()
        assert result_path == recorder.filename
        assert recorder.is_recording is False
        mock_save.assert_called_once()

def test_stop_without_recording(mock_pyaudio):
    recorder = AudioRecorder()
    assert recorder.stop_recording() is None

def test_save_file_writes_wav(mock_pyaudio, tmp_path):
    test_file = str(tmp_path / "output.wav")
    recorder = AudioRecorder(test_file)
    recorder.frames = [b"\x00" * 1024]
    
    # Mockeamos wave.open para verificar que se intenta escribir el archivo
    with patch("recorder.wave.open") as mock_wave_open:
        recorder._save_file()
        mock_wave_open.assert_called_once_with(recorder.filename, "wb")

def test_cleanup(mock_pyaudio):
    recorder = AudioRecorder()
    recorder.cleanup()
    mock_pyaudio.terminate.assert_called_once()
