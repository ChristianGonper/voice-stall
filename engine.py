import json
import logging
import os
import re
import time

from faster_whisper import WhisperModel

from transcription_models import TranscriptionResult


logger = logging.getLogger(__name__)


class STTEngine:
    def __init__(self, model_size=None, device="cuda", compute_type=None):
        base_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(base_dir, "config.json")
        self.default_config_path = os.path.join(base_dir, "config.default.json")
        self.config = {}
        self._config_mtime = None
        self._dictionary_patterns = []
        self.load_config(force=True)

        if model_size:
            self.model_size = model_size

        target_compute = compute_type or self.config.get("engine", {}).get("compute_type", "float16")

        import torch

        if not torch.cuda.is_available():
            logger.warning("CUDA no detectado, usando CPU.")
            device = "cpu"
            target_compute = "int8"

        logger.info("Cargando modelo %s en %s (%s)...", self.model_size, device, target_compute)
        self.model = WhisperModel(self.model_size, device=device, compute_type=target_compute)
        logger.info("Motor cargado y listo.")

    def load_config(self, force=False):
        default_config = {
            "config_version": 1,
            "engine": {
                "model_size": "large-v3-turbo",
                "language": "auto",
                "compute_type": "float16",
                "initial_prompt": "Dictado profesional en espanol de Espana. Usa puntuacion correcta.",
                "profile": "balanced",
            },
            "dictionary": {},
        }
        config_source = self.config_path if os.path.exists(self.config_path) else self.default_config_path
        file_mtime = os.path.getmtime(config_source) if os.path.exists(config_source) else None
        if not force and self.config and file_mtime == self._config_mtime:
            return False

        if os.path.exists(config_source):
            try:
                with open(config_source, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                logger.exception("Error cargando configuracion.")
                self.config = default_config
        else:
            self.config = default_config

        self.config.setdefault("config_version", 1)
        engine_cfg = self.config.get("engine", {})
        self.model_size = engine_cfg.get("model_size", "large-v3-turbo")
        lang_cfg = str(engine_cfg.get("language", "auto")).strip().lower()
        if lang_cfg in ("", "auto", "none", "null"):
            self.language = None
        elif lang_cfg == "en":
            self.language = "en"
        else:
            self.language = "es"
        self.initial_prompt = engine_cfg.get("initial_prompt", "Dictado en espanol.")
        self.profile = engine_cfg.get("profile", "balanced")
        self.dictionary = self.config.get("dictionary", {})
        self._dictionary_patterns = self._build_dictionary_patterns(self.dictionary)
        self._config_mtime = file_mtime
        return True

    def _build_dictionary_patterns(self, dictionary):
        patterns = []
        for key in sorted(dictionary.keys(), key=len, reverse=True):
            escaped_key = re.escape(key)
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

        if not self.dictionary:
            return text

        processed_text = text
        for pattern, value in self._dictionary_patterns:
            processed_text = pattern.sub(value, processed_text)

        return processed_text

    def transcribe(self, audio_path):
        language = self.language or "auto"
        if not os.path.exists(audio_path):
            return TranscriptionResult(text="", raw_text="", language=language)

        self.load_config()
        transcribe_params = self._get_transcribe_params()
        t0 = time.perf_counter()

        current_prompt = self.initial_prompt
        if self.language == "en":
            current_prompt = "Technical dictation in English. Professional tone."

        lang_label = self.language.upper() if self.language else "AUTO"
        logger.info("Transcribiendo en %s (%s)...", lang_label, self.profile)
        segments, _info = self.model.transcribe(
            audio_path,
            beam_size=transcribe_params["beam_size"],
            temperature=transcribe_params["temperature"],
            language=self.language,
            initial_prompt=current_prompt,
            vad_filter=transcribe_params["vad_filter"],
            vad_parameters=transcribe_params["vad_parameters"],
            condition_on_previous_text=False,
        )

        full_text = []
        for segment in segments:
            full_text.append(segment.text)

        raw_text = "".join(full_text).strip()
        text_with_dict = self.apply_dictionary(raw_text)

        total_ms = (time.perf_counter() - t0) * 1000
        return TranscriptionResult(
            text=text_with_dict,
            raw_text=raw_text,
            language=self.language or "auto",
            timings={"engine_total_ms": round(total_ms, 2)},
        )
