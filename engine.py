import json
import os
import re
from faster_whisper import WhisperModel

class STTEngine:
    def __init__(self, model_size=None, device="cuda", compute_type=None):
        base_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(base_dir, "config.json")
        self.default_config_path = os.path.join(base_dir, "config.default.json")
        self.config = {}
        self._config_mtime = None
        self._dictionary_patterns = []
        self.load_config(force=True)
        
        # Priorizar parámetros del constructor si se pasan, si no usar config
        if model_size:
            self.model_size = model_size
        
        target_compute = compute_type or self.config.get("engine", {}).get("compute_type", "float16")

        # Intentamos usar CUDA si está disponible
        import torch
        if not torch.cuda.is_available():
            print("CUDA no detectado, usando CPU...")
            device = "cpu"
            target_compute = "int8"
            
        print(f"Cargando modelo {self.model_size} en {device} ({target_compute})...")
        self.model = WhisperModel(self.model_size, device=device, compute_type=target_compute)
        print("Motor cargado y listo.")

    def load_config(self, force=False):
        default_config = {
            "engine": {
                "model_size": "large-v3-turbo",
                "language": "auto",
                "compute_type": "float16",
                "initial_prompt": "Dictado profesional en español de España. Usa puntuación correcta.",
                "use_llm": False,
                "profile": "balanced"
            },
            "dictionary": {}
        }
        config_source = self.config_path if os.path.exists(self.config_path) else self.default_config_path
        file_mtime = os.path.getmtime(config_source) if os.path.exists(config_source) else None
        if not force and self.config and file_mtime == self._config_mtime:
            return False

        if os.path.exists(config_source):
            try:
                with open(config_source, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error cargando configuracion: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
        engine_cfg = self.config.get("engine", {})
        self.model_size = engine_cfg.get("model_size", "large-v3-turbo")
        lang_cfg = str(engine_cfg.get("language", "auto")).strip().lower()
        if lang_cfg in ("", "auto", "none", "null"):
            self.language = None
        elif lang_cfg == "en":
            self.language = "en"
        else:
            self.language = "es"
        self.initial_prompt = engine_cfg.get("initial_prompt", "Dictado en español.")
        self.use_llm = engine_cfg.get("use_llm", False)
        self.profile = engine_cfg.get("profile", "balanced")
        self.dictionary = self.config.get("dictionary", {})
        self._dictionary_patterns = self._build_dictionary_patterns(self.dictionary)
        self._config_mtime = file_mtime
        return True

    def _build_dictionary_patterns(self, dictionary):
        patterns = []
        for key in sorted(dictionary.keys(), key=len, reverse=True):
            escaped_key = re.escape(key)
            # Reemplazo por coincidencia completa para evitar sustituciones parciales.
            pattern = re.compile(rf"(?<!\w){escaped_key}(?!\w)", re.IGNORECASE)
            patterns.append((pattern, dictionary[key]))
        return patterns

    def _get_transcribe_params(self):
        profiles = {
            "fast": {
                "beam_size": 1,
                "temperature": 0.25,
                "vad_filter": True,
                "vad_parameters": dict(min_silence_duration_ms=500),
            },
            "accurate": {
                "beam_size": 2,
                "temperature": 0.15,
                "vad_filter": True,
                "vad_parameters": dict(min_silence_duration_ms=300),
            },
            "balanced": {
                "beam_size": 1,
                "temperature": 0.2,
                "vad_filter": True,
                "vad_parameters": dict(min_silence_duration_ms=400),
            },
        }
        return profiles.get(self.profile, profiles["balanced"])

    def apply_dictionary(self, text):
        if not text:
            return text
            
        # 1. Detección de Comandos
        text_lower = text.lower().strip()
        
        # Comando: ABRIR WEB
        if text_lower.startswith("abre"):
            target = text_lower.replace("abre", "").strip()
            # Mapeo simple de nombres a URLs
            web_map = {
                "google": "https://www.google.com",
                "chat gpt": "https://chat.openai.com",
                "gemini": "https://gemini.google.com",
                "github": "https://www.github.com",
                "notion": "https://www.notion.so"
            }
            url = web_map.get(target, f"https://www.google.com/search?q={target}")
            import webbrowser
            webbrowser.open(url)
            return f"Opening {target}..."

        if not self.dictionary:
            return text
            
        processed_text = text
        for pattern, value in self._dictionary_patterns:
            processed_text = pattern.sub(value, processed_text)
            
        return processed_text

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            return ""

        self.load_config()
        transcribe_params = self._get_transcribe_params()
        
        # Ajuste dinámico de prompt según idioma
        current_prompt = self.initial_prompt # Por defecto Spanglish del config.json
        if self.language == "en":
            current_prompt = "Technical dictation in English. Professional tone."

        lang_label = self.language.upper() if self.language else "AUTO"
        print(f"Transcribiendo en {lang_label} ({self.profile})...")
        segments, info = self.model.transcribe(
            audio_path, 
            beam_size=transcribe_params["beam_size"], 
            temperature=transcribe_params["temperature"],
            language=self.language,
            initial_prompt=current_prompt,
            vad_filter=transcribe_params["vad_filter"],
            vad_parameters=transcribe_params["vad_parameters"],
            condition_on_previous_text=False
        )

        full_text = []
        for segment in segments:
            full_text.append(segment.text)

        raw_text = "".join(full_text).strip()
        text_with_dict = self.apply_dictionary(raw_text)
        
        # Solo usamos el LLM si está activo y no es un comando directo
        if self.use_llm and not text_with_dict.lower().startswith(("abre", "calcula")):
            return self.refine_with_llm(text_with_dict)
        
        return text_with_dict

    def refine_with_llm(self, text):
        if not text or len(text) < 5:
            return text
            
        import requests
        url = "http://localhost:11434/api/generate"
        # Prompt EXTREMADAMENTE estricto para evitar Markdown o basura de código
        prompt = (
            f"Instrucción: Eres un corrector de dictado. Limpia y mejora el texto siguiente. "
            f"REGLAS CRÍTICAS: 1. Devuelve SOLAMENTE el texto corregido. 2. NO uses Markdown, ni negritas, ni comillas invertidas. "
            f"3. NO añadas barras invertidas ni saltos de línea. 4. Devuelve texto plano y fluido.\n\n"
            f"Texto: {text}"
        )
        
        try:
            response = requests.post(url, json={
                "model": "qwen2.5-coder:3b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3} # Menos creatividad = más estabilidad
            }, timeout=5)
            if response.status_code == 200:
                refined = response.json().get("response", "").strip()
                # Limpieza extra de seguridad: quitar Markdown y saltos de línea locos
                refined = refined.replace("`", "").replace("*", "").replace("\\", "")
                return refined if refined else text
        except Exception as e:
            print(f"Ollama error: {e}")
            
        return text
