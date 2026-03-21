import json
import logging
import os
from datetime import datetime


logger = logging.getLogger(__name__)


class AppStorage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "config.json")
        self.default_config_path = os.path.join(base_dir, "config.default.json")
        self.history_path = os.path.join(base_dir, "dictation_history.json")
        self.timing_log_path = os.path.join(base_dir, "timings.log")

    def default_config(self):
        fallback = {
            "config_version": 1,
            "engine": {
                "model_size": "large-v3-turbo",
                "language": "auto",
                "compute_type": "float16",
                "initial_prompt": (
                    "Dictado profesional en español con terminología técnica en inglés "
                    "(Spanglish). Soporta Python, Matlab y conceptos de ingeniería. "
                    "Transcribe solo lo dicho. Mantén los términos en inglés exactamente "
                    "como se pronuncian y no los traduzcas al español. No añadas palabras "
                    "de cierre ni fórmulas de cortesía (por ejemplo, gracias)."
                ),
                "profile": "balanced",
            },
            "app": {
                "hotkey": "ctrl+alt+s",
                "history_limit": 5,
                "timing_log_max_kb": 512,
                "diagnostic_mode": False,
            },
            "dictionary": {},
        }
        if not os.path.exists(self.default_config_path):
            return fallback
        try:
            with open(self.default_config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            logger.exception("No se pudo cargar config.default.json, usando fallback.")
            return fallback
        if not isinstance(cfg, dict):
            return fallback
        return self._merge_config(fallback, cfg)

    def _merge_config(self, base, override):
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value
        return merged

    def load_config(self):
        default_cfg = self.default_config()
        config_source = self.config_path if os.path.exists(self.config_path) else self.default_config_path
        if not os.path.exists(config_source):
            return default_cfg
        try:
            with open(config_source, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            logger.exception("No se pudo cargar configuracion, usando defaults.")
            return default_cfg
        if not isinstance(cfg, dict):
            return default_cfg
        return self._merge_config(default_cfg, cfg)

    def save_config(self, cfg):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

    def load_history(self, history_limit):
        if not os.path.exists(self.history_path):
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data[:history_limit]
        except Exception:
            logger.exception("No se pudo cargar historial.")
            return []
        return []

    def save_history(self, history):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def push_history(self, history, text, history_limit):
        entry = {"ts": datetime.now().isoformat(timespec="seconds"), "text": text}
        updated = [entry] + list(history)
        updated = updated[: int(history_limit)]
        self.save_history(updated)
        return updated

    def _rotate_timing_log_if_needed(self, max_kb):
        max_bytes = int(max_kb) * 1024
        if not os.path.exists(self.timing_log_path):
            return
        if os.path.getsize(self.timing_log_path) <= max_bytes:
            return
        backup_path = f"{self.timing_log_path}.1"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.replace(self.timing_log_path, backup_path)

    def log_timing(self, payload, diagnostic_mode, max_kb):
        if not diagnostic_mode:
            return
        log_payload = dict(payload)
        log_payload["ts"] = datetime.now().isoformat(timespec="seconds")
        try:
            self._rotate_timing_log_if_needed(max_kb)
            with open(self.timing_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_payload, ensure_ascii=False) + "\n")
        except Exception:
            logger.exception("No se pudo escribir timing log.")
