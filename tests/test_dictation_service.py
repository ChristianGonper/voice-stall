from dictation_service import DictationService
from transcription_models import TranscriptionResult


class FakeEngine:
    def __init__(self, result):
        self._result = result

    def transcribe(self, _audio_file):
        return self._result


def test_transcribe_returns_cycle_with_text_and_timing():
    result = TranscriptionResult(text="hola", raw_text="hola", language="es")
    engine = FakeEngine(result=result)
    svc = DictationService(engine)

    cycle = svc.transcribe("temp.wav")

    assert cycle.text == "hola"
    assert cycle.transcribe_ms >= 0.0
