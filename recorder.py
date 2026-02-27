import os
import threading
import wave
import logging

import pyaudio

logger = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self, filename="temp_audio.wav"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper prefiere 16kHz
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.thread = None
        self.record_error = None

    def _record(self):
        stream = None
        try:
            stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    self.record_error = e
                    logger.exception("Error leyendo audio.")
                    break
        except Exception as e:
            self.record_error = e
            logger.exception("Error abriendo microfono.")
        finally:
            self.is_recording = False
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    logger.exception("Error cerrando stream.")

    def start_recording(self):
        if self.is_recording:
            return False

        logger.info("Grabando...")
        self.record_error = None
        self.is_recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record, daemon=True)
        self.thread.start()

        return True

    def stop_recording(self):
        if not self.is_recording and (self.thread is None or not self.thread.is_alive()):
            return None

        logger.info("Deteniendo grabacion...")
        self.is_recording = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        if self.record_error is not None:
            logger.error("Grabacion abortada: %s", self.record_error)
            return None

        if not self.frames:
            logger.warning("No se capturo audio.")
            return None

        try:
            self._save_file()
        except Exception:
            logger.exception("Error guardando audio.")
            return None

        return self.filename

    def _save_file(self):
        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self.frames))

    def cleanup(self):
        self.is_recording = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)

        try:
            self.p.terminate()
        except Exception:
            logger.exception("Error terminando PyAudio.")

        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except Exception:
                logger.exception("Error borrando temporal.")
