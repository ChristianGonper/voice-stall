import json
import os
import sys
import threading
import time
import traceback
from typing import Any

import pyperclip
try:
    from pynput import keyboard
except Exception:  # pragma: no cover - depends on desktop environment
    keyboard = None

from app_storage import AppStorage
from dictation_service import DictationService
from engine import STTEngine
from recorder import AudioRecorder


class SidecarServer:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.storage = AppStorage(base_dir)
        self.recorder = AudioRecorder()

        self.engine = None
        self.dictation_service = None

        self.cfg = self.storage.load_config()
        self.app_cfg = self.cfg.get("app", {})

        self.hotkey_listener = None
        self.state_tracker = None
        self.pressed_keys = set()
        self.key_press_times: dict[str, float] = {}
        self.state_lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.engine_init_lock = threading.Lock()
        self.is_recording = False
        self.is_processing = False
        self.is_pasting = False
        self.last_trigger_time = 0.0
        self.current_status = "loading"
        self.current_status_message = "Cargando motor..."

        self._start_state_tracker()
        self._restart_hotkey_listener()
        self._preload_engine()

    def _start_state_tracker(self):
        """Starts a background listener to track the REAL physical state of modifier keys."""
        if keyboard is None:
            return

        def on_press(key):
            try:
                now = time.monotonic()
                # Store the canonical name of the key
                if hasattr(key, 'vk'):
                    self.pressed_keys.add(key.vk)
                else:
                    self.pressed_keys.add(key)
                for token in self._key_to_tokens(key):
                    self.key_press_times[token] = now
            except Exception:
                pass

        def on_release(key):
            try:
                if hasattr(key, 'vk'):
                    self.pressed_keys.discard(key.vk)
                else:
                    self.pressed_keys.discard(key)
            except Exception:
                pass

        self.state_tracker = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.state_tracker.daemon = True
        self.state_tracker.start()

    def _write_json(self, payload: dict[str, Any]):
        encoded = json.dumps(payload, ensure_ascii=False)
        with self.write_lock:
            sys.stdout.write(encoded + "\n")
            sys.stdout.flush()

    def _emit_event(self, event: str, payload: dict[str, Any]):
        self._write_json({"event": event, "payload": payload})

    def _emit_status(self, state: str, message: str):
        self.current_status = state
        self.current_status_message = message
        self._emit_event("status", {"state": state, "message": message})

    def _normalize_hotkey(self, value: str) -> str:
        normalized = str(value or "ctrl+alt+s").strip().lower().replace(" ", "")
        normalized = normalized.replace("control", "ctrl").replace("option", "alt").replace("command", "cmd")
        if normalized.count("+") < 1:
            return "ctrl+alt+s"
        return normalized

    def _hotkey_to_pynput(self, hotkey: str) -> str:
        # Avoid using brackets for modifiers if possible, pynput handles ctrl, alt, shift natively in strings
        # But for GlobalHotKeys, the canonical way is often <ctrl>+<alt>+s on Windows for better modifier detection
        token_map = {"ctrl": "<ctrl>", "alt": "<alt>", "shift": "<shift>", "cmd": "<cmd>"}
        parts = []
        for t in hotkey.split("+"):
            if not t: continue
            parts.append(token_map.get(t, t))
        return "+".join(parts)

    def _key_to_tokens(self, key: Any) -> set[str]:
        tokens: set[str] = set()
        vk = getattr(key, "vk", None)
        char = getattr(key, "char", None)
        if isinstance(char, str) and char:
            tokens.add(char.lower())
        if isinstance(vk, int):
            vk_map = {
                16: "shift",
                17: "ctrl",
                18: "alt",
                91: "cmd",
                92: "cmd",
            }
            mapped = vk_map.get(vk)
            if mapped:
                tokens.add(mapped)
            if 65 <= vk <= 90:
                tokens.add(chr(vk).lower())
            elif 48 <= vk <= 57:
                tokens.add(chr(vk))

        if keyboard is not None:
            key_cls = getattr(keyboard, "Key", None)
            if key_cls is not None:
                alias_map = {
                    getattr(key_cls, "ctrl", None): "ctrl",
                    getattr(key_cls, "ctrl_l", None): "ctrl",
                    getattr(key_cls, "ctrl_r", None): "ctrl",
                    getattr(key_cls, "alt", None): "alt",
                    getattr(key_cls, "alt_l", None): "alt",
                    getattr(key_cls, "alt_r", None): "alt",
                    getattr(key_cls, "shift", None): "shift",
                    getattr(key_cls, "shift_l", None): "shift",
                    getattr(key_cls, "shift_r", None): "shift",
                    getattr(key_cls, "cmd", None): "cmd",
                    getattr(key_cls, "cmd_l", None): "cmd",
                    getattr(key_cls, "cmd_r", None): "cmd",
                }
                mapped = alias_map.get(key)
                if mapped:
                    tokens.add(mapped)

        return tokens

    def _is_hotkey_token_pressed(self, token: str, pressed_keys: set[Any] | None) -> bool:
        if pressed_keys is None:
            return True

        normalized = token.strip().lower()
        if not normalized:
            return True

        variants: list[Any] = []

        if normalized == "ctrl":
            variants.extend(["ctrl", "ctrl_l", "ctrl_r", 17])
        elif normalized == "alt":
            variants.extend(["alt", "alt_l", "alt_r", 18])
        elif normalized == "shift":
            variants.extend(["shift", "shift_l", "shift_r", 16])
        elif normalized == "cmd":
            variants.extend(["cmd", "cmd_l", "cmd_r", 91, 92])
        else:
            variants.extend([normalized, normalized.upper()])
            if len(normalized) == 1:
                variants.extend([ord(normalized.lower()), ord(normalized.upper())])

        if keyboard is not None:
            key_cls = getattr(keyboard, "Key", None)
            if key_cls is not None:
                for name in [v for v in variants if isinstance(v, str)]:
                    key_value = getattr(key_cls, name, None)
                    if key_value is not None:
                        variants.append(key_value)

            key_code_cls = getattr(keyboard, "KeyCode", None)
            if key_code_cls is not None and len(normalized) == 1:
                try:
                    variants.append(key_code_cls.from_char(normalized.lower()))
                    variants.append(key_code_cls.from_char(normalized.upper()))
                except Exception:
                    pass

        return any(variant in pressed_keys for variant in variants)

    def _was_hotkey_token_pressed_recently(self, token: str, now: float, window_s: float = 0.35) -> bool:
        normalized = token.strip().lower()
        if normalized in {"", "ctrl", "alt", "shift", "cmd"}:
            return True
        key_press_times = getattr(self, "key_press_times", {})
        last_pressed = key_press_times.get(normalized)
        if last_pressed is None:
            return False
        return (now - last_pressed) <= window_s

    def _on_hotkey_trigger(self):
        now = time.time()
        # Debounce: prevent triggering twice within 800ms
        if now - self.last_trigger_time < 0.8:
            return
        
        # PHYSICAL VERIFICATION:
        # pynput.GlobalHotKeys is prone to "ghost" triggers on Windows if a key release was missed.
        # We check our own state_tracker to confirm the full hotkey is REALLY pressed.
        app_cfg = getattr(self, "app_cfg", {})
        hotkey_str = app_cfg.get("hotkey", "ctrl+alt+s") if isinstance(app_cfg, dict) else "ctrl+alt+s"
        pressed_keys = getattr(self, "pressed_keys", None)
        monotonic_now = time.monotonic()
        for token in hotkey_str.split("+"):
            if not self._is_hotkey_token_pressed(token, pressed_keys):
                return
            if not self._was_hotkey_token_pressed_recently(token, monotonic_now):
                return

        if self.is_processing or self.is_pasting:
            return

        self.last_trigger_time = now
        
        try:
            self.toggle_dictation()
        except Exception as exc:  # pragma: no cover - safety path
            self._emit_status("error", f"Error hotkey: {exc}")

    def _restart_hotkey_listener(self):
        if keyboard is None:
            self.hotkey_listener = None
            return

        hotkey = self._normalize_hotkey(self.app_cfg.get("hotkey", "ctrl+alt+s"))
        self.app_cfg["hotkey"] = hotkey
        if self.hotkey_listener is not None:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None

        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({self._hotkey_to_pynput(hotkey): self._on_hotkey_trigger})
            self.hotkey_listener.start()
        except Exception as exc:
            self.hotkey_listener = None
            self._emit_status("error", f"Hotkey invalida: {exc}")

    def _ensure_engine(self):
        with self.engine_init_lock:
            if self.engine is not None and self.dictation_service is not None:
                return

            self._emit_status("loading", "Cargando motor...")
            try:
                self.engine = STTEngine()
                self.dictation_service = DictationService(self.engine)
            except Exception as exc:
                self.engine = None
                self.dictation_service = None
                self._emit_status("error", f"No se pudo cargar el motor: {exc}")
                raise

            self._emit_status("idle", "Listo para dictar")

    def _preload_engine(self):
        try:
            self._ensure_engine()
        except Exception:
            # Keep the sidecar responsive so the UI can still open and show the error state.
            pass

    def _compute_recent_metrics(self, last_n: int = 5) -> dict[str, Any]:
        timing_log_path = self.storage.timing_log_path
        if not os.path.exists(timing_log_path):
            return {"count": 0, "avg_total_ms": 0.0, "avg_transcribe_ms": 0.0, "avg_paste_ms": 0.0}

        rows = []
        try:
            with open(timing_log_path, "r", encoding="utf-8") as file_handle:
                for line in file_handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if row.get("event") == "dictation_cycle":
                        rows.append(row)
        except Exception:
            return {"count": 0, "avg_total_ms": 0.0, "avg_transcribe_ms": 0.0, "avg_paste_ms": 0.0}

        recent = rows[-int(last_n) :]
        if not recent:
            return {"count": 0, "avg_total_ms": 0.0, "avg_transcribe_ms": 0.0, "avg_paste_ms": 0.0}

        count = len(recent)
        return {
            "count": count,
            "avg_total_ms": sum(float(r.get("total_ms", 0.0)) for r in recent) / count,
            "avg_transcribe_ms": sum(float(r.get("transcribe_ms", 0.0)) for r in recent) / count,
            "avg_paste_ms": sum(float(r.get("paste_ms", 0.0)) for r in recent) / count,
        }

    def _push_history(self, text: str):
        limit = int(self.app_cfg.get("history_limit", 5))
        self.storage.push_history(self.storage.load_history(limit), text, limit)

    def _log_timing(self, payload: dict[str, Any]):
        self.storage.log_timing(
            payload=payload,
            diagnostic_mode=bool(self.app_cfg.get("diagnostic_mode", False)),
            max_kb=int(self.app_cfg.get("timing_log_max_kb", 512)),
        )
        self._emit_event("diag", payload)

    def start_recording(self) -> dict[str, Any]:
        with self.state_lock:
            if self.is_processing:
                return {"status": "processing", "message": "Procesando audio"}
            if self.is_recording:
                return {"status": "recording", "message": "Ya estaba grabando"}

        self._ensure_engine()
        started = self.recorder.start_recording()
        if not started:
            return {"status": "error", "message": "No se pudo iniciar grabacion"}

        with self.state_lock:
            self.is_recording = True
        self._emit_status("recording", "Escuchando")
        return {"status": "recording", "message": "Escuchando"}

    def stop_and_transcribe(self) -> dict[str, Any]:
        with self.state_lock:
            if not self.is_recording:
                return {"status": "idle", "message": "No habia grabacion activa"}
            self.is_recording = False
            self.is_processing = True

        # SAFETY DELAY: Let the OS process the hotkey release events before the CPU spike
        time.sleep(0.1)

        self._emit_status("processing", "Procesando audio")

        audio_file = None
        t0 = time.perf_counter()
        transcribe_ms = 0.0
        paste_ms = 0.0
        text = ""
        try:
            audio_file = self.recorder.stop_recording()
            if not audio_file:
                return {"status": "idle", "message": "No se capturo audio"}

            self._ensure_engine()
            cycle = self.dictation_service.transcribe(audio_file)
            transcribe_ms = cycle.transcribe_ms
            text = cycle.text

            if text:
                t_paste0 = time.perf_counter()
                pyperclip.copy(text)
                time.sleep(0.05)
                
                try:
                    self.is_pasting = True
                    import pyautogui
                    pyautogui.hotkey("ctrl", "v")
                    pyautogui.press("space")
                    paste_ms = (time.perf_counter() - t_paste0) * 1000
                except Exception:
                    # Likely headless or display issues in CI
                    paste_ms = 0.0
                finally:
                    self.is_pasting = False
                
                self._push_history(text)
                self._emit_event("transcription", {"text": text, "ts": time.strftime("%H:%M:%S")})

            return {"status": "idle", "message": "Listo para dictar", "text": text}
        finally:
            if audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

            total_ms = (time.perf_counter() - t0) * 1000
            self._log_timing(
                {
                    "event": "dictation_cycle",
                    "transcribe_ms": round(transcribe_ms, 2),
                    "paste_ms": round(paste_ms, 2),
                    "total_ms": round(total_ms, 2),
                    "chars": len(text),
                }
            )
            with self.state_lock:
                self.is_processing = False
            self._emit_status("idle", "Listo para dictar")

    def toggle_dictation(self) -> dict[str, Any]:
        with self.state_lock:
            currently_recording = self.is_recording
        if currently_recording:
            return self.stop_and_transcribe()
        return self.start_recording()

    def load_app_state(self) -> dict[str, Any]:
        self.cfg = self.storage.load_config()
        self.app_cfg = self.cfg.get("app", {})
        history = self.storage.load_history(int(self.app_cfg.get("history_limit", 5)))
        metrics = self._compute_recent_metrics(5)
        return {
            "config": self.cfg,
            "history": history,
            "metrics": metrics,
            "status": self.current_status,
            "status_message": self.current_status_message,
        }

    def save_config(self, config: dict[str, Any]) -> dict[str, Any]:
        previous_engine_cfg = dict(self.cfg.get("engine", {}))
        self.storage.save_config(config)
        self.cfg = self.storage.load_config()
        self.app_cfg = self.cfg.get("app", {})
        self._restart_hotkey_listener()
        current_engine_cfg = dict(self.cfg.get("engine", {}))

        if previous_engine_cfg != current_engine_cfg:
            with self.engine_init_lock:
                self.engine = None
                self.dictation_service = None
            self._preload_engine()
        elif self.engine is not None:
            self.engine.load_config(force=True)
        return {"ok": True}

    def set_hotkey(self, hotkey: str) -> dict[str, Any]:
        self.cfg = self.storage.load_config()
        app_cfg = self.cfg.setdefault("app", {})
        app_cfg["hotkey"] = self._normalize_hotkey(hotkey)
        self.cfg["app"] = app_cfg
        self.storage.save_config(self.cfg)
        self.app_cfg = app_cfg
        self._restart_hotkey_listener()
        return {"ok": True, "hotkey": app_cfg["hotkey"]}

    def get_history(self, limit: int) -> list[dict[str, Any]]:
        return self.storage.load_history(int(limit))

    def get_recent_metrics(self, last_n: int) -> dict[str, Any]:
        return self._compute_recent_metrics(int(last_n))

    def handle(self, method: str, params: dict[str, Any]) -> Any:
        if method == "health":
            return {"ok": True}
        if method == "load_app_state":
            return self.load_app_state()
        if method == "save_config":
            return self.save_config(params.get("config", {}))
        if method == "start_recording":
            return self.start_recording()
        if method == "stop_and_transcribe":
            return self.stop_and_transcribe()
        if method == "toggle_dictation":
            return self.toggle_dictation()
        if method == "set_hotkey":
            return self.set_hotkey(str(params.get("hotkey", "ctrl+alt+s")))
        if method == "get_history":
            return self.get_history(int(params.get("limit", 10)))
        if method == "get_recent_metrics":
            return self.get_recent_metrics(int(params.get("last_n", 5)))
        raise ValueError(f"Metodo no soportado: {method}")

    def close(self):
        try:
            if self.hotkey_listener is not None:
                self.hotkey_listener.stop()
        except Exception:
            pass
        try:
            self.recorder.cleanup()
        except Exception:
            pass


def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    server = SidecarServer(os.path.dirname(os.path.abspath(__file__)))
    try:
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue
            request_id = None
            try:
                req = json.loads(line)
                request_id = req.get("id")
                method = req.get("method")
                params = req.get("params") or {}
                result = server.handle(method, params)
                server._write_json({"id": request_id, "ok": True, "result": result})
            except Exception as exc:
                error_payload = {
                    "id": request_id,
                    "ok": False,
                    "error": {
                        "code": "internal_error",
                        "message": str(exc),
                        "traceback": traceback.format_exc(limit=2),
                    },
                }
                server._write_json(error_payload)
    finally:
        server.close()


if __name__ == "__main__":
    main()
