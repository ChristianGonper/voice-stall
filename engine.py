from faster_whisper import WhisperModel
import os

class STTEngine:
    def __init__(self, model_size="large-v3-turbo", device="cuda", compute_type="float16"):
        """
        model_size: large-v3-turbo, medium, small, base
        device: cpu, cuda
        compute_type: int8, float16 (cuda), float32
        """
        # Intentamos usar CUDA si está disponible, si no volvemos a CPU
        import torch
        if not torch.cuda.is_available():
            print("CUDA no detectado, usando CPU...")
            device = "cpu"
            compute_type = "int8"
            
        print(f"Cargando modelo {model_size} en {device} ({compute_type})...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.initial_prompt = (
            "Este es un dictado en español de España. "
            "Por favor, incluye puntuación correcta, comas, puntos y mayúsculas. "
            "El tono es profesional y claro."
        )

    def transcribe(self, audio_path):
        """
        Transcribe un archivo de audio y devuelve el texto.
        """
        if not os.path.exists(audio_path):
            return ""

        print("Transcribiendo...")
        segments, info = self.model.transcribe(
            audio_path, 
            beam_size=1, 
            language="es", 
            initial_prompt=self.initial_prompt
        )

        full_text = []
        for segment in segments:
            full_text.append(segment.text)

        return "".join(full_text).strip()
