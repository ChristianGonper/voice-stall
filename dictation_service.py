import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class DictationCycle:
    text: str
    transcribe_ms: float


class DictationService:
    def __init__(self, engine):
        self.engine = engine
        self._engine_lock = threading.Lock()

    def transcribe(self, audio_file):
        with self._engine_lock:
            t0 = time.perf_counter()
            result = self.engine.transcribe(audio_file)
            transcribe_ms = (time.perf_counter() - t0) * 1000
        return DictationCycle(text=result.text, transcribe_ms=transcribe_ms)
