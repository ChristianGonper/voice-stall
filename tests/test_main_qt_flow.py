import os
import threading
from types import SimpleNamespace

from dictation_service import DictationCycle
from main_qt import VoiceStallQtApp


class _Emitter:
    def __init__(self):
        self.events = []

    def emit(self, status, message):
        self.events.append((status, message))


def _build_app_stub():
    app = VoiceStallQtApp.__new__(VoiceStallQtApp)
    app.state_lock = threading.Lock()
    app.is_processing = False
    app.is_recording = False
    app.engine = object()
    app.dictation_service = None
    app.app_config = {"history_limit": 5, "diagnostic_mode": True, "timing_log_max_kb": 512}
    app.signals = SimpleNamespace(status_changed=_Emitter())
    return app


def test_toggle_dictation_ignores_when_processing(mocker):
    app = _build_app_stub()
    app.is_processing = True
    app.start_recording = mocker.Mock()
    app.stop_recording = mocker.Mock()

    VoiceStallQtApp.toggle_dictation(app)

    app.start_recording.assert_not_called()
    app.stop_recording.assert_not_called()


def test_toggle_dictation_routes_start_and_stop(mocker):
    app = _build_app_stub()
    app.start_recording = mocker.Mock()
    app.stop_recording = mocker.Mock()

    app.is_recording = False
    VoiceStallQtApp.toggle_dictation(app)
    app.start_recording.assert_called_once()

    app.start_recording.reset_mock()
    app.is_recording = True
    VoiceStallQtApp.toggle_dictation(app)
    app.stop_recording.assert_called_once()


def test_process_audio_pastes_and_logs(tmp_path, mocker):
    app = _build_app_stub()
    app.dictation_service = SimpleNamespace(transcribe=lambda _p: DictationCycle(text="hola", transcribe_ms=12.5))
    app._push_history = mocker.Mock()
    app._log_timing = mocker.Mock()

    mocker.patch("main_qt.pyperclip.copy")
    mocker.patch("main_qt.pyautogui.hotkey")
    mocker.patch("main_qt.pyautogui.press")
    mocker.patch("main_qt.time.sleep")

    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"demo")
    app.is_processing = True

    VoiceStallQtApp.process_audio(app, str(audio_file))

    app._push_history.assert_called_once_with("hola")
    app._log_timing.assert_called_once()
    assert not os.path.exists(audio_file)
    assert app.is_processing is False
    assert app.signals.status_changed.events[-1][0] == "idle"


def test_process_audio_handles_transcription_error(tmp_path, mocker):
    app = _build_app_stub()
    app.dictation_service = SimpleNamespace(transcribe=mocker.Mock(side_effect=RuntimeError("boom")))
    app._push_history = mocker.Mock()
    app._log_timing = mocker.Mock()

    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"demo")
    app.is_processing = True

    VoiceStallQtApp.process_audio(app, str(audio_file))

    assert app._push_history.call_count == 0
    assert app._log_timing.call_count == 1
    assert app.signals.status_changed.events[0][0] == "error"
    assert app.signals.status_changed.events[-1][0] == "idle"
