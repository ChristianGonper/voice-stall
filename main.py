import ctypes
import json
import os
import sys
import threading
import time
from datetime import datetime

import pyautogui
import pyperclip
import tkinter as tk
from pynput import keyboard

from engine import STTEngine
from recorder import AudioRecorder


class VoiceStallApp:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.history_path = os.path.join(self.base_dir, "dictation_history.json")
        self.timing_log_path = os.path.join(self.base_dir, "timings.log")

        self.recorder = AudioRecorder()
        self.engine = None
        self.is_recording = False
        self.is_processing = False
        self.icon_image = None
        self.logo_image = None
        self.temp_config = None
        self.hotkey_listener = None
        self.history = []
        self.app_config = self._load_app_settings()

        self.root = tk.Tk()
        self.root.title("Voice Stall")
        self.root.geometry("344x136+20+20")
        self.root.overrideredirect(False)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.bg_color, self.frame_color, self.header_color = "#07090C", "#0F131A", "#121821"
        self.border_idle, self.idle_color = "#1E2633", "#768AA3"
        self.recording_color, self.processing_color, self.refining_color = "#FF4757", "#54A0FF", "#A55EE1"
        self.listening_color, self.text_color, self.subtitle_color = "#2ED573", "#F1F2F6", "#A4B0BE"
        self.hotkey_bg, self.hotkey_fg, self.brand_color, self.accent_idle = "#1C2533", "#CED6E0", "#70A1FF", "#2F3542"

        self.root.configure(bg=self.bg_color)
        self.configure_icon()

        self.outer_frame = tk.Frame(self.root, bg="#06080C", padx=1, pady=1)
        self.outer_frame.pack(expand=True, fill="both")
        self.main_frame = tk.Frame(
            self.outer_frame, bg=self.frame_color, highlightthickness=1, highlightbackground=self.border_idle
        )
        self.main_frame.pack(expand=True, fill="both")

        self.header = tk.Frame(self.main_frame, bg=self.header_color, height=44)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        self.header_left = tk.Frame(self.header, bg=self.header_color)
        self.header_left.pack(side="left", padx=10, pady=6)
        self.logo_label = tk.Label(
            self.header_left,
            image=self.logo_image,
            text="" if self.logo_image else "VS",
            fg=self.brand_color,
            bg=self.header_color,
            font=("Bahnschrift SemiBold", 11),
        )
        self.logo_label.pack(side="left", padx=(0, 8))
        self.brand_block = tk.Frame(self.header_left, bg=self.header_color)
        self.brand_block.pack(side="left")
        tk.Label(
            self.brand_block, text="Voice Stall", fg=self.text_color, bg=self.header_color, font=("Bahnschrift SemiBold", 11)
        ).pack(anchor="w")
        tk.Label(self.brand_block, text="Minimal Pro", fg="#7D8CA4", bg=self.header_color, font=("Bahnschrift", 8)).pack(anchor="w")

        self.header_right = tk.Frame(self.header, bg=self.header_color)
        self.header_right.pack(side="right", padx=(0, 10), pady=7)
        self.mode_badge = tk.Label(
            self.header_right, text="IDLE", fg=self.hotkey_fg, bg=self.hotkey_bg, font=("Bahnschrift SemiBold", 8), padx=8, pady=2
        )
        self.mode_badge.pack(side="left", padx=(0, 8))
        self.drag_hint = tk.Label(self.header_right, text="⋮⋮", fg="#5F6E87", bg=self.header_color, font=("Bahnschrift", 10))
        self.drag_hint.pack(side="left", padx=(5, 0))
        self.settings_btn = tk.Label(
            self.header_right, text="⚙", fg="#5F6E87", bg=self.header_color, font=("Bahnschrift", 12), cursor="hand2"
        )
        self.settings_btn.pack(side="left", padx=(8, 0))
        self.settings_btn.bind("<Button-1>", lambda e: self.open_dictionary_editor())

        self.accent_line = tk.Frame(self.main_frame, bg=self.accent_idle, height=2)
        self.accent_line.pack(fill="x", side="top")
        self.status_container = tk.Frame(self.main_frame, bg=self.frame_color)
        self.status_container.pack(expand=True, fill="both", padx=12, pady=(10, 9))
        self.indicator = tk.Label(
            self.status_container, text="●", fg=self.idle_color, bg=self.frame_color, font=("Bahnschrift SemiBold", 14)
        )
        self.indicator.pack(side="left", anchor="n", pady=(1, 0))
        self.status_text_block = tk.Frame(self.status_container, bg=self.frame_color)
        self.status_text_block.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.status_text = tk.Label(
            self.status_text_block, text="Listo para dictar", fg=self.subtitle_color, bg=self.frame_color, font=("Bahnschrift SemiBold", 10)
        )
        self.status_text.pack(anchor="w")
        self.hint_text = tk.Label(self.status_text_block, text="", fg="#7E8EA8", bg=self.frame_color, font=("Bahnschrift", 8))
        self.hint_text.pack(anchor="w", pady=(1, 0))
        self.hotkey_badge = tk.Label(
            self.status_container, text="", fg=self.hotkey_fg, bg=self.hotkey_bg, font=("Bahnschrift SemiBold", 8), padx=8, pady=3
        )
        self.hotkey_badge.pack(side="right", anchor="center")

        for widget in (self.header, self.header_left, self.brand_block, self.header_right, self.status_container):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        self._refresh_hotkey_ui()
        self._start_hotkey_listener()
        self.root.after(0, self.configure_taskbar_visibility)
        threading.Thread(target=self._load_engine, daemon=True).start()

    def _default_config(self):
        return {
            "engine": {
                "model_size": "large-v3-turbo",
                "language": "auto",
                "compute_type": "float16",
                "initial_prompt": "Dictado profesional en español con terminología técnica en inglés (Spanglish).",
                "use_llm": False,
                "profile": "balanced",
            },
            "app": {
                "hotkey": "ctrl+alt+s",
                "history_limit": 5,
                "timing_log_max_kb": 512,
            },
            "dictionary": {},
        }

    def _load_app_settings(self):
        cfg = self._safe_load_config()
        app_cfg = cfg.setdefault("app", {})
        app_cfg.setdefault("hotkey", "ctrl+alt+s")
        app_cfg.setdefault("history_limit", 5)
        app_cfg.setdefault("timing_log_max_kb", 512)
        cfg["app"] = app_cfg
        self._save_config(cfg)
        self.history = self._load_history(app_cfg["history_limit"])
        return app_cfg

    def _safe_load_config(self):
        default_cfg = self._default_config()
        if not os.path.exists(self.config_path):
            return default_cfg
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            return default_cfg
        cfg.setdefault("engine", default_cfg["engine"])
        cfg.setdefault("dictionary", {})
        cfg.setdefault("app", default_cfg["app"])
        return cfg

    def _save_config(self, cfg):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

    def _normalize_hotkey(self, hotkey_value):
        normalized = hotkey_value.strip().lower().replace(" ", "")
        normalized = normalized.replace("control", "ctrl")
        normalized = normalized.replace("option", "alt")
        if normalized.count("+") < 1:
            return "ctrl+alt+s"
        return normalized

    def _hotkey_to_pynput(self, hotkey_value):
        token_map = {"ctrl": "<ctrl>", "alt": "<alt>", "shift": "<shift>"}
        tokens = [t for t in hotkey_value.split("+") if t]
        mapped = [token_map.get(t, t) for t in tokens]
        return "+".join(mapped)

    def _hotkey_to_label(self, hotkey_value):
        return " + ".join(part.upper() for part in hotkey_value.split("+"))

    def _refresh_hotkey_ui(self):
        hk_label = self._hotkey_to_label(self.app_config.get("hotkey", "ctrl+alt+s"))
        self.hotkey_badge.config(text=hk_label)
        self.hint_text.config(text=f"Pulsa {hk_label}")

    def _start_hotkey_listener(self):
        hotkey_value = self._normalize_hotkey(self.app_config.get("hotkey", "ctrl+alt+s"))
        self.app_config["hotkey"] = hotkey_value
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({self._hotkey_to_pynput(hotkey_value): self.toggle_dictation})
            self.hotkey_listener.start()
        except Exception as e:
            self.hotkey_listener = None
            self.root.after(0, lambda: self.status_text.config(text=f"Hotkey inválida: {e}", fg=self.recording_color))

    def _restart_hotkey_listener(self):
        if self.hotkey_listener is not None:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        self._start_hotkey_listener()
        self._refresh_hotkey_ui()

    def _load_history(self, history_limit):
        if not os.path.exists(self.history_path):
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data[:history_limit]
        except Exception:
            return []
        return []

    def _save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"No se pudo guardar historial: {e}")

    def _push_history(self, text):
        limit = int(self.app_config.get("history_limit", 5))
        entry = {"ts": datetime.now().isoformat(timespec="seconds"), "text": text}
        self.history.insert(0, entry)
        self.history = self.history[:limit]
        self._save_history()

    def _rotate_timing_log_if_needed(self):
        max_kb = int(self.app_config.get("timing_log_max_kb", 512))
        max_bytes = max_kb * 1024
        if not os.path.exists(self.timing_log_path):
            return
        if os.path.getsize(self.timing_log_path) <= max_bytes:
            return
        backup_path = f"{self.timing_log_path}.1"
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.replace(self.timing_log_path, backup_path)
        except Exception as e:
            print(f"No se pudo rotar log de tiempos: {e}")

    def _log_timing(self, payload):
        payload["ts"] = datetime.now().isoformat(timespec="seconds")
        self._rotate_timing_log_if_needed()
        try:
            with open(self.timing_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"No se pudo escribir timing log: {e}")

    def _get_recent_timing_stats(self, last_n=5):
        if not os.path.exists(self.timing_log_path):
            return {"count": 0, "avg_total_ms": 0.0, "avg_transcribe_ms": 0.0, "avg_paste_ms": 0.0}

        rows = []
        try:
            with open(self.timing_log_path, "r", encoding="utf-8") as f:
                for line in f:
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

        recent = rows[-last_n:]
        if not recent:
            return {"count": 0, "avg_total_ms": 0.0, "avg_transcribe_ms": 0.0, "avg_paste_ms": 0.0}

        count = len(recent)
        return {
            "count": count,
            "avg_total_ms": sum(float(r.get("total_ms", 0.0)) for r in recent) / count,
            "avg_transcribe_ms": sum(float(r.get("transcribe_ms", 0.0)) for r in recent) / count,
            "avg_paste_ms": sum(float(r.get("paste_ms", 0.0)) for r in recent) / count,
        }

    def _load_engine(self):
        self.root.after(0, lambda: self.update_ui("loading"))
        try:
            self.engine = STTEngine()
            self.root.after(0, lambda: self.update_ui("idle"))
        except Exception as e:
            self.engine = None
            print(f"Error cargando motor: {e}")
            self.root.after(0, lambda: self.update_ui("error"))
            self.root.after(0, lambda: self.status_text.config(text=f"Error cargando motor: {e}", fg=self.recording_color))

    def configure_icon(self):
        ico = os.path.join(self.base_dir, "voice_stall_icon.ico")
        png = os.path.join(self.base_dir, "voice_stall_icon.png")
        try:
            if sys.platform == "win32" and os.path.exists(ico):
                self.root.iconbitmap(default=ico)
            if os.path.exists(png):
                self.icon_image = tk.PhotoImage(file=png)
                self.root.iconphoto(True, self.icon_image)
                self.logo_image = self.icon_image.subsample(14, 14)
        except Exception:
            pass

    def update_ui(self, status):
        if status == "idle":
            self.indicator.config(fg=self.idle_color)
            self.status_text.config(text="Listo para dictar", fg=self.subtitle_color)
            self.mode_badge.config(text="IDLE", fg=self.hotkey_fg, bg=self.hotkey_bg)
            self.main_frame.config(highlightbackground=self.border_idle)
        elif status == "recording":
            self.indicator.config(fg=self.recording_color)
            self.status_text.config(text="Escuchando...", fg=self.recording_color)
            self.mode_badge.config(text="REC", fg="#FFD8D9", bg="#3A1D24")
            self.main_frame.config(highlightbackground=self.recording_color)
        elif status == "processing":
            self.indicator.config(fg=self.processing_color)
            self.status_text.config(text="Procesando...", fg=self.processing_color)
            self.mode_badge.config(text="PROC", fg="#FFE8BC", bg="#3A2B14")
            self.main_frame.config(highlightbackground=self.processing_color)
        elif status == "refining":
            self.indicator.config(fg=self.refining_color)
            self.status_text.config(text="IA Refinando...", fg=self.refining_color)
            self.mode_badge.config(text="AI", fg="#E0C3FC", bg="#2D1B4D")
            self.main_frame.config(highlightbackground=self.refining_color)
        elif status == "loading":
            self.indicator.config(fg=self.processing_color)
            self.status_text.config(text="Cargando motor...", fg=self.processing_color)
            self.mode_badge.config(text="LOAD", fg="#FFE8BC", bg="#3A2B14")
            self.main_frame.config(highlightbackground=self.processing_color)
        elif status == "error":
            self.indicator.config(fg=self.recording_color)
            self.mode_badge.config(text="ERR", fg="#FFD8D9", bg="#3A1D24")
            self.main_frame.config(highlightbackground=self.recording_color)

    def toggle_dictation(self):
        if self.is_processing:
            return
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.engine is None:
            self.update_ui("loading")
            return
        if self.recorder.start_recording():
            self.is_recording = True
            self.update_ui("recording")

    def stop_recording(self):
        self.is_recording = False
        self.is_processing = True
        self.update_ui("processing")
        audio_file = self.recorder.stop_recording()
        if not audio_file:
            self.is_processing = False
            self.update_ui("idle")
            return
        threading.Thread(target=self.process_audio, args=(audio_file,), daemon=True).start()

    def process_audio(self, audio_file):
        t0 = time.perf_counter()
        transcribe_ms = 0
        paste_ms = 0
        refine_started = False
        text = ""
        old_llm = self.engine.use_llm if self.engine else False
        try:
            if self.engine is None:
                return
            self.engine.use_llm = False
            t_transcribe0 = time.perf_counter()
            text = self.engine.transcribe(audio_file)
            transcribe_ms = (time.perf_counter() - t_transcribe0) * 1000
            if text:
                t_paste0 = time.perf_counter()
                pyperclip.copy(text)
                time.sleep(0.05)
                pyautogui.hotkey("ctrl", "v")
                pyautogui.press("space")
                paste_ms = (time.perf_counter() - t_paste0) * 1000
                self._push_history(text)
                if old_llm and not text.lower().startswith("abre"):
                    refine_started = True
                    threading.Thread(target=self.refine_and_replace, args=(text,), daemon=True).start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.engine is not None:
                self.engine.use_llm = old_llm
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
                    "refine_started": refine_started,
                }
            )
            self.is_processing = False
            self.root.after(0, lambda: self.update_ui("idle"))

    def refine_and_replace(self, original_text):
        self.root.after(0, lambda: self.update_ui("refining"))
        t0 = time.perf_counter()
        try:
            refined = self.engine.refine_with_llm(original_text)
            if refined and refined.strip() != original_text.strip():
                time.sleep(0.4)
                chars = len(original_text) + 1
                for _ in range(chars):
                    pyautogui.press("backspace")
                pyperclip.copy(refined)
                time.sleep(0.05)
                pyautogui.hotkey("ctrl", "v")
                pyautogui.press("space")
                self._push_history(refined)
        except Exception as e:
            print(f"Error en refinado: {e}")
        finally:
            total_ms = (time.perf_counter() - t0) * 1000
            self._log_timing({"event": "refine_cycle", "total_ms": round(total_ms, 2), "chars": len(original_text)})
            self.root.after(0, lambda: self.update_ui("idle"))

    def open_dictionary_editor(self):
        editor = tk.Toplevel(self.root)
        editor.title("Configuración")
        editor.geometry("420x700")
        editor.configure(bg=self.bg_color)
        editor.attributes("-topmost", True)
        editor.resizable(False, False)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.temp_config = json.load(f)
        self.temp_config.setdefault("engine", {})
        self.temp_config.setdefault("dictionary", {})
        self.temp_config.setdefault("app", {})
        self.temp_config["engine"].setdefault("profile", "balanced")
        self.temp_config["app"].setdefault("hotkey", self.app_config.get("hotkey", "ctrl+alt+s"))
        self.temp_config["app"].setdefault("history_limit", 5)
        self.temp_config["app"].setdefault("timing_log_max_kb", 512)

        header_f = tk.Frame(editor, bg=self.header_color, pady=15)
        header_f.pack(fill="x")
        tk.Label(
            header_f,
            text="Configuración y Diccionario",
            fg=self.brand_color,
            bg=self.header_color,
            font=("Bahnschrift SemiBold", 13),
        ).pack()

        toggle_f = tk.Frame(editor, bg=self.bg_color, pady=10)
        toggle_f.pack(fill="x", padx=15)

        def cycle_language(current):
            order = ["auto", "es", "en"]
            current = str(current).lower()
            if current not in order:
                current = "auto"
            return order[(order.index(current) + 1) % len(order)]

        def cycle_profile(current):
            order = ["fast", "balanced", "accurate"]
            current = str(current).lower()
            if current not in order:
                current = "balanced"
            return order[(order.index(current) + 1) % len(order)]

        def switch_temp(feature):
            if feature == "llm":
                self.temp_config["engine"]["use_llm"] = not self.temp_config["engine"].get("use_llm", False)
            elif feature == "lang":
                cur = self.temp_config["engine"].get("language", "auto")
                self.temp_config["engine"]["language"] = cycle_language(cur)
            elif feature == "model":
                cur = self.temp_config["engine"].get("model_size", "large-v3-turbo")
                self.temp_config["engine"]["model_size"] = "base" if cur == "large-v3-turbo" else "large-v3-turbo"
            elif feature == "profile":
                cur = self.temp_config["engine"].get("profile", "balanced")
                self.temp_config["engine"]["profile"] = cycle_profile(cur)
            refresh_ui()

        btn_llm = tk.Button(toggle_f, text="Qwen LLM", command=lambda: switch_temp("llm"), font=("Bahnschrift", 9), borderwidth=0, padx=10)
        btn_llm.pack(side="left", padx=5)
        btn_lang = tk.Button(toggle_f, text="Idioma", command=lambda: switch_temp("lang"), font=("Bahnschrift", 9), borderwidth=0, padx=10)
        btn_lang.pack(side="left", padx=5)
        btn_model = tk.Button(toggle_f, text="Modelo", command=lambda: switch_temp("model"), font=("Bahnschrift", 9), borderwidth=0, padx=10)
        btn_model.pack(side="left", padx=5)
        btn_profile = tk.Button(toggle_f, text="Perfil", command=lambda: switch_temp("profile"), font=("Bahnschrift", 9), borderwidth=0, padx=10)
        btn_profile.pack(side="left", padx=5)

        hotkey_card = tk.Frame(editor, bg=self.frame_color, padx=12, pady=10)
        hotkey_card.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(hotkey_card, text="Hotkey", fg=self.subtitle_color, bg=self.frame_color, font=("Bahnschrift", 9)).pack(anchor="w")
        hotkey_entry = tk.Entry(
            hotkey_card,
            bg=self.bg_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            borderwidth=0,
            font=("Bahnschrift", 10),
            highlightthickness=1,
            highlightbackground=self.border_idle,
        )
        hotkey_entry.pack(fill="x", ipady=3, pady=(5, 0))
        hotkey_entry.insert(0, self.temp_config["app"].get("hotkey", "ctrl+alt+s"))
        tk.Label(
            hotkey_card,
            text="Formato: ctrl+alt+s, ctrl+shift+v, alt+x",
            fg="#7E8EA8",
            bg=self.frame_color,
            font=("Bahnschrift", 8),
        ).pack(anchor="w", pady=(4, 0))

        def refresh_ui():
            llm_on = self.temp_config["engine"].get("use_llm", False)
            language = str(self.temp_config["engine"].get("language", "auto")).upper()
            model_large = self.temp_config["engine"].get("model_size", "large-v3-turbo") == "large-v3-turbo"
            profile = str(self.temp_config["engine"].get("profile", "balanced")).upper()
            btn_llm.config(
                text=f"Qwen: {'ON' if llm_on else 'OFF'}",
                bg=self.listening_color if llm_on else self.hotkey_bg,
                fg=self.bg_color if llm_on else self.text_color,
            )
            btn_lang.config(text=f"Lang: {language}", bg=self.brand_color, fg=self.bg_color)
            btn_model.config(
                text=f"Mod: {'LARGE' if model_large else 'BASE'}",
                bg=self.refining_color if model_large else self.idle_color,
                fg=self.text_color,
            )
            btn_profile.config(text=f"Perf: {profile}", bg="#34495E", fg=self.text_color)

        refresh_ui()

        def apply():
            old_model = self.engine.model_size if self.engine else ""
            normalized_hotkey = self._normalize_hotkey(hotkey_entry.get())
            self.temp_config["app"]["hotkey"] = normalized_hotkey

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.temp_config, f, indent=2, ensure_ascii=False)

            self.app_config = self.temp_config["app"]
            self._restart_hotkey_listener()
            self.history = self._load_history(int(self.app_config.get("history_limit", 5)))

            new_model = self.temp_config["engine"].get("model_size", "large-v3-turbo")
            if old_model != new_model:
                threading.Thread(target=self._load_engine, daemon=True).start()
            elif self.engine:
                self.engine.load_config(force=True)

            self.root.after(0, lambda: self.status_text.config(text="CONFIGURACIÓN APLICADA", fg=self.listening_color))
            self.root.after(2000, lambda: self.update_ui("idle"))
            editor.destroy()

        tk.Button(
            editor,
            text="GUARDAR Y APLICAR CAMBIOS",
            command=apply,
            bg=self.brand_color,
            fg=self.bg_color,
            font=("Bahnschrift SemiBold", 10),
            pady=10,
            borderwidth=0,
        ).pack(fill="x", padx=15, pady=10)

        input_card = tk.Frame(editor, bg=self.frame_color, padx=20, pady=20)
        input_card.pack(fill="x", padx=15, pady=10)

        def create_entry(parent, label):
            frame = tk.Frame(parent, bg=self.frame_color)
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, fg=self.subtitle_color, bg=self.frame_color, font=("Bahnschrift", 9)).pack(side="left")
            entry = tk.Entry(
                frame,
                bg=self.bg_color,
                fg=self.text_color,
                insertbackground=self.text_color,
                borderwidth=0,
                font=("Bahnschrift", 10),
                highlightthickness=1,
                highlightbackground=self.border_idle,
            )
            entry.pack(side="right", fill="x", expand=True, ipady=3)
            return entry

        say_entry = create_entry(input_card, "Si digo:")
        write_entry = create_entry(input_card, "Escribir:")

        def save_dict():
            key = say_entry.get().strip().lower()
            value = write_entry.get().strip()
            if key and value:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                cfg.setdefault("dictionary", {})
                cfg["dictionary"][key] = value
                self._save_config(cfg)
                refresh_list()
                say_entry.delete(0, tk.END)
                write_entry.delete(0, tk.END)

        tk.Button(
            input_card,
            text="Añadir al Diccionario",
            command=save_dict,
            bg=self.brand_color,
            fg=self.bg_color,
            font=("Bahnschrift SemiBold", 10),
            pady=8,
        ).pack(fill="x", pady=(15, 0))

        list_container = tk.Frame(editor, bg=self.bg_color)
        list_container.pack(fill="both", expand=True, padx=15, pady=(0, 8))
        canvas = tk.Canvas(list_container, bg=self.bg_color, highlightthickness=0)
        scroll_frame = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=370)
        canvas.pack(side="left", fill="both", expand=True)

        def refresh_list():
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            with open(self.config_path, "r", encoding="utf-8") as f:
                items = json.load(f).get("dictionary", {})
            for key, value in items.items():
                item = tk.Frame(scroll_frame, bg=self.frame_color, pady=8, padx=12)
                item.pack(fill="x", pady=3)
                tk.Label(item, text=f"{key} -> {value}", fg=self.text_color, bg=self.frame_color, font=("Bahnschrift", 10)).pack(side="left")
                delete_btn = tk.Label(item, text="X", fg="#FF6B72", bg=self.frame_color, cursor="hand2")
                delete_btn.pack(side="right")
                delete_btn.bind("<Button-1>", lambda e, k=key: delete_item(k))
            scroll_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        def delete_item(key):
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if key in cfg.get("dictionary", {}):
                del cfg["dictionary"][key]
                self._save_config(cfg)
                refresh_list()

        refresh_list()

        history_card = tk.Frame(editor, bg=self.frame_color, padx=12, pady=10)
        history_card.pack(fill="x", padx=15, pady=(0, 12))
        tk.Label(history_card, text="Historial reciente (5)", fg=self.subtitle_color, bg=self.frame_color, font=("Bahnschrift", 9)).pack(anchor="w")
        for item in self.history[:5]:
            snippet = item.get("text", "").strip().replace("\n", " ")
            snippet = snippet if len(snippet) <= 64 else snippet[:61] + "..."
            tk.Label(
                history_card,
                text=f"{item.get('ts', '--')} | {snippet}",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
                anchor="w",
                justify="left",
            ).pack(fill="x", pady=(2, 0))

        stats = self._get_recent_timing_stats(last_n=5)
        stats_card = tk.Frame(editor, bg=self.frame_color, padx=12, pady=10)
        stats_card.pack(fill="x", padx=15, pady=(0, 12))
        tk.Label(stats_card, text="Promedio rendimiento (últimos 5)", fg=self.subtitle_color, bg=self.frame_color, font=("Bahnschrift", 9)).pack(anchor="w")
        if stats["count"] == 0:
            tk.Label(
                stats_card,
                text="Aún no hay datos de dictado.",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
            ).pack(anchor="w", pady=(2, 0))
        else:
            tk.Label(
                stats_card,
                text=f"Ciclos analizados: {stats['count']}",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
            ).pack(anchor="w", pady=(2, 0))
            tk.Label(
                stats_card,
                text=f"Total medio: {stats['avg_total_ms']:.1f} ms",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
            ).pack(anchor="w")
            tk.Label(
                stats_card,
                text=f"STT medio: {stats['avg_transcribe_ms']:.1f} ms",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
            ).pack(anchor="w")
            tk.Label(
                stats_card,
                text=f"Pegado medio: {stats['avg_paste_ms']:.1f} ms",
                fg=self.text_color,
                bg=self.frame_color,
                font=("Bahnschrift", 8),
            ).pack(anchor="w")

    def configure_taskbar_visibility(self):
        if sys.platform != "win32":
            return
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VoiceStall.App")
            hwnd = self.root.winfo_id()
            exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, (exstyle & ~0x00000080) | 0x00040000)
            self.root.withdraw()
            self.root.after(10, self.root.deiconify)
        except Exception:
            pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def shutdown(self):
        try:
            if self.hotkey_listener is not None:
                self.hotkey_listener.stop()
        except Exception:
            pass
        try:
            self.recorder.cleanup()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = VoiceStallApp()
    app.run()
