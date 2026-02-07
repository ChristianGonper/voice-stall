import os
import threading
import wave

import pyaudio


class AudioRecorder:
    def __init__(self, filename="temp_audio.wav"):
        self.filename = filename
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
                    print(f"Error leyendo audio: {e}")
                    break
        except Exception as e:
            self.record_error = e
            print(f"Error abriendo micrófono: {e}")
        finally:
            self.is_recording = False
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    print(f"Error cerrando stream: {e}")

    def start_recording(self):
        if self.is_recording:
            return False

        print("Grabando...")
        self.record_error = None
        self.is_recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record, daemon=True)
        self.thread.start()

        return True

    def stop_recording(self):
        if not self.is_recording and (self.thread is None or not self.thread.is_alive()):
            return None

        print("Deteniendo grabación...")
        self.is_recording = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        if self.record_error is not None:
            print(f"Grabación abortada: {self.record_error}")
            return None

        if not self.frames:
            print("No se capturó audio.")
            return None

        try:
            self._save_file()
        except Exception as e:
            print(f"Error guardando audio: {e}")
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
        except Exception as e:
            print(f"Error terminando PyAudio: {e}")

        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except Exception as e:
                print(f"Error borrando temporal: {e}")
