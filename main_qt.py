import json
import os
import sys
import threading
import time
from datetime import datetime

import pyautogui
import pyperclip

if sys.platform == "win32":
    qt_rule = "qt.qpa.window=false"
    current_rules = os.environ.get("QT_LOGGING_RULES", "").strip()
    if not current_rules:
        os.environ["QT_LOGGING_RULES"] = qt_rule
    elif qt_rule not in current_rules:
        os.environ["QT_LOGGING_RULES"] = f"{current_rules};{qt_rule}"

from PySide6.QtCore import QObject, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from pynput import keyboard

from engine import STTEngine
from recorder import AudioRecorder


class SignalBus(QObject):
    status_changed = Signal(str, str)
    hotkey_changed = Signal(str)


class SettingsDialog(QDialog):
    def __init__(self, cfg, history, timing_log_path, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.history = history
        self.timing_log_path = timing_log_path
        self.setWindowTitle("Voice Stall - Ajustes")
        self.setModal(True)
        self.setFixedSize(700, 760)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("Configuracion de dictado")
        title.setObjectName("title")
        root.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        app_cfg = self.cfg.setdefault("app", {})
        engine_cfg = self.cfg.setdefault("engine", {})

        self.hotkey_input = QLineEdit(app_cfg.get("hotkey", "ctrl+alt+s"))
        self.hotkey_input.setPlaceholderText("ctrl+alt+s")
        form.addRow("Hotkey", self.hotkey_input)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["large-v3-turbo", "base"])
        self.model_combo.setCurrentText(engine_cfg.get("model_size", "large-v3-turbo"))
        form.addRow("Modelo", self.model_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["auto", "es", "en"])
        self.lang_combo.setCurrentText(str(engine_cfg.get("language", "auto")).lower())
        form.addRow("Idioma", self.lang_combo)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["fast", "balanced", "accurate"])
        self.profile_combo.setCurrentText(str(engine_cfg.get("profile", "balanced")).lower())
        form.addRow("Perfil", self.profile_combo)

        self.use_llm = QCheckBox("Refinar con LLM local (Ollama)")
        self.use_llm.setChecked(bool(engine_cfg.get("use_llm", False)))
        form.addRow("LLM", self.use_llm)

        self.diag_mode = QCheckBox("Activar metricas de diagnostico")
        self.diag_mode.setChecked(bool(app_cfg.get("diagnostic_mode", False)))
        form.addRow("Diagnostico", self.diag_mode)

        self.history_limit = QSpinBox()
        self.history_limit.setRange(1, 20)
        self.history_limit.setValue(int(app_cfg.get("history_limit", 5)))
        form.addRow("Historial", self.history_limit)

        root.addLayout(form)

        hint = QLabel("Aplica cambios sin reiniciar. Si cambia el modelo, se recarga el motor.")
        hint.setObjectName("hint")
        root.addWidget(hint)

        lower = QHBoxLayout()
        lower.setSpacing(10)

        dict_box = QGroupBox("Diccionario")
        dict_layout = QVBoxLayout(dict_box)
        self.dict_list = QListWidget()
        dict_layout.addWidget(self.dict_list)

        dict_inputs = QHBoxLayout()
        self.dict_key = QLineEdit()
        self.dict_key.setPlaceholderText("Si digo...")
        self.dict_value = QLineEdit()
        self.dict_value.setPlaceholderText("Escribir...")
        dict_inputs.addWidget(self.dict_key)
        dict_inputs.addWidget(self.dict_value)
        dict_layout.addLayout(dict_inputs)

        dict_buttons = QHBoxLayout()
        add_dict_btn = QPushButton("Añadir")
        del_dict_btn = QPushButton("Borrar seleccionado")
        add_dict_btn.clicked.connect(self.add_dictionary_item)
        del_dict_btn.clicked.connect(self.delete_dictionary_item)
        dict_buttons.addWidget(add_dict_btn)
        dict_buttons.addWidget(del_dict_btn)
        dict_layout.addLayout(dict_buttons)

        history_box = QGroupBox("Historial reciente")
        history_layout = QVBoxLayout(history_box)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        history_layout.addWidget(self.history_text)

        lower.addWidget(dict_box, 3)
        lower.addWidget(history_box, 2)
        root.addLayout(lower)

        metrics_box = QGroupBox("Metricas de rendimiento")
        metrics_layout = QVBoxLayout(metrics_box)
        self.metrics_summary = QLabel("Sin datos")
        self.metrics_summary.setObjectName("hint")
        metrics_layout.addWidget(self.metrics_summary)

        self.total_bar = QProgressBar()
        self.stt_bar = QProgressBar()
        self.paste_bar = QProgressBar()
        for bar in (self.total_bar, self.stt_bar, self.paste_bar):
            bar.setMinimum(0)
            bar.setMaximum(3000)
            bar.setTextVisible(True)
            metrics_layout.addWidget(bar)

        refresh_metrics_btn = QPushButton("Refrescar metricas")
        refresh_metrics_btn.clicked.connect(self.refresh_metrics_view)
        metrics_layout.addWidget(refresh_metrics_btn)
        root.addWidget(metrics_box)

        row = QHBoxLayout()
        row.addStretch()
        cancel_btn = QPushButton("Cancelar")
        save_btn = QPushButton("Guardar")
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.accept)
        row.addWidget(cancel_btn)
        row.addWidget(save_btn)
        root.addLayout(row)

        self.setStyleSheet(
            """
            QDialog { background: #101822; color: #d7e4f1; }
            QLabel#title { font-size: 16px; font-weight: 700; color: #f5f9ff; }
            QLabel#hint { color: #8ca4bd; font-size: 11px; }
            QLineEdit, QComboBox, QSpinBox, QListWidget, QTextEdit {
                background: #0f1824; color: #d7e4f1; border: 1px solid #2d3f53; border-radius: 8px; padding: 5px;
            }
            QGroupBox {
                border: 1px solid #2d3f53; border-radius: 10px; margin-top: 8px; padding-top: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #9fb8d1; }
            QCheckBox { color: #d7e4f1; }
            QPushButton {
                background: #1b2838; color: #d7e4f1; border: 1px solid #355070;
                border-radius: 8px; padding: 6px 10px; font-weight: 600;
            }
            QPushButton:hover { background: #26364b; }
            """
        )
        self.refresh_dictionary_list()
        self.refresh_history_view()
        self.refresh_metrics_view()

    def refresh_dictionary_list(self):
        self.dict_list.clear()
        dictionary = self.cfg.setdefault("dictionary", {})
        for key in sorted(dictionary.keys(), key=lambda x: x.lower()):
            self.dict_list.addItem(f"{key} -> {dictionary[key]}")

    def refresh_history_view(self):
        rows = []
        for item in self.history[:10]:
            ts = item.get("ts", "--")
            text = str(item.get("text", "")).replace("\n", " ").strip()
            if len(text) > 90:
                text = f"{text[:87]}..."
            rows.append(f"{ts}\n{text}\n")
        self.history_text.setPlainText("\n".join(rows) if rows else "Sin entradas de historial.")

    def add_dictionary_item(self):
        key = self.dict_key.text().strip().lower()
        value = self.dict_value.text().strip()
        if not key or not value:
            return
        dictionary = self.cfg.setdefault("dictionary", {})
        dictionary[key] = value
        self.cfg["dictionary"] = dictionary
        self.dict_key.clear()
        self.dict_value.clear()
        self.refresh_dictionary_list()

    def delete_dictionary_item(self):
        current = self.dict_list.currentItem()
        if current is None:
            return
        raw = current.text()
        key = raw.split(" -> ", 1)[0].strip().lower()
        dictionary = self.cfg.setdefault("dictionary", {})
        if key in dictionary:
            del dictionary[key]
        self.cfg["dictionary"] = dictionary
        self.refresh_dictionary_list()

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

    def _set_metric_bar(self, bar, value, label):
        clamped = max(0, min(int(value), bar.maximum()))
        bar.setValue(clamped)
        bar.setFormat(f"{label}: {value:.1f} ms")

    def refresh_metrics_view(self):
        stats = self._get_recent_timing_stats(last_n=5)
        diag_enabled = bool(self.cfg.get("app", {}).get("diagnostic_mode", False))
        if stats["count"] == 0:
            self.metrics_summary.setText(
                f"Diagnostico: {'ON' if diag_enabled else 'OFF'} | Sin datos. Realiza dictados con diagnostico activo."
            )
            self._set_metric_bar(self.total_bar, 0.0, "Total")
            self._set_metric_bar(self.stt_bar, 0.0, "STT")
            self._set_metric_bar(self.paste_bar, 0.0, "Pegado")
            return

        self.metrics_summary.setText(
            f"Diagnostico: {'ON' if diag_enabled else 'OFF'} | Ciclos: {stats['count']} (ultimos 5)"
        )
        self._set_metric_bar(self.total_bar, stats["avg_total_ms"], "Total")
        self._set_metric_bar(self.stt_bar, stats["avg_transcribe_ms"], "STT")
        self._set_metric_bar(self.paste_bar, stats["avg_paste_ms"], "Pegado")

    def result_config(self):
        app_cfg = self.cfg.setdefault("app", {})
        engine_cfg = self.cfg.setdefault("engine", {})

        app_cfg["hotkey"] = self.hotkey_input.text().strip() or "ctrl+alt+s"
        app_cfg["history_limit"] = int(self.history_limit.value())
        app_cfg.setdefault("timing_log_max_kb", 512)
        app_cfg["diagnostic_mode"] = bool(self.diag_mode.isChecked())

        engine_cfg["model_size"] = self.model_combo.currentText()
        engine_cfg["language"] = self.lang_combo.currentText()
        engine_cfg["profile"] = self.profile_combo.currentText()
        engine_cfg["use_llm"] = bool(self.use_llm.isChecked())

        self.cfg["app"] = app_cfg
        self.cfg["engine"] = engine_cfg
        self.cfg.setdefault("dictionary", {})
        return self.cfg


class VoiceStallQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.history_path = os.path.join(self.base_dir, "dictation_history.json")
        self.timing_log_path = os.path.join(self.base_dir, "timings.log")
        self.cli_diagnostic_forced = any(arg in ("--diag", "--diagnostic") for arg in sys.argv[1:])

        self.recorder = AudioRecorder()
        self.engine = None
        self.is_recording = False
        self.is_processing = False
        self.hotkey_listener = None
        self.history = []

        self.app_config = self._load_app_settings()
        if self.cli_diagnostic_forced:
            self.app_config["diagnostic_mode"] = True

        self.signals = SignalBus()
        self.signals.status_changed.connect(self._apply_status)
        self.signals.hotkey_changed.connect(self._set_hotkey_text)
        self.current_status = "loading"
        self.status_base_text = "Cargando motor"
        self._dots = 0

        self._build_ui()
        self._setup_animations()
        self._start_hotkey_listener()
        threading.Thread(target=self._load_engine, daemon=True).start()

    def _build_ui(self):
        self.setWindowTitle("Voice Stall - Neo")
        self.setFixedSize(460, 250)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        icon_path = os.path.join(self.base_dir, "voice_stall_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        container = QWidget(self)
        self.setCentralWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)
        root.addWidget(self.card)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.brand = QLabel("Voice Stall")
        self.brand.setObjectName("brand")
        self.tag = QLabel("2026")
        self.tag.setObjectName("tag")
        self.settings_btn = QPushButton("Ajustes")
        self.settings_btn.setObjectName("settings")
        self.settings_btn.clicked.connect(self.open_settings)
        self.mode = QLabel("IDLE")
        self.mode.setObjectName("mode")
        header.addWidget(self.brand)
        header.addWidget(self.tag)
        header.addStretch()
        header.addWidget(self.settings_btn)
        header.addWidget(self.mode)
        card_layout.addLayout(header)

        self.status = QLabel("Cargando motor...")
        self.status.setObjectName("status")
        card_layout.addWidget(self.status)

        self.hint = QLabel("Hotkey: CTRL + ALT + S")
        self.hint.setObjectName("hint")
        card_layout.addWidget(self.hint)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setObjectName("progress")
        card_layout.addWidget(self.progress)

        self.action_btn = QPushButton("Iniciar dictado")
        self.action_btn.setObjectName("action")
        self.action_btn.clicked.connect(self.toggle_dictation)
        card_layout.addWidget(self.action_btn)

        footer = QLabel("Motor STT local | Privado")
        footer.setObjectName("footer")
        card_layout.addWidget(footer)

        self.setStyleSheet(
            """
            QWidget { background: #0b1118; color: #d7e4f1; font-family: "Segoe UI"; }
            QFrame#card {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #111926, stop:1 #0e1520);
                border: 1px solid #223246;
                border-radius: 16px;
            }
            QLabel#brand { font-size: 20px; font-weight: 700; color: #f5f9ff; }
            QLabel#tag {
                background: #1a2638; color: #94b8ff; border: 1px solid #355070;
                border-radius: 10px; padding: 2px 8px; font-weight: 600;
            }
            QLabel#mode {
                background: #1c2838; color: #b8c9dc; border: 1px solid #364a62;
                border-radius: 10px; padding: 3px 10px; font-weight: 700;
            }
            QLabel#status { font-size: 17px; font-weight: 600; color: #ecf3ff; }
            QLabel#hint { color: #8ca4bd; font-size: 12px; }
            QLabel#footer { color: #6f869e; font-size: 11px; }
            QPushButton#action {
                background: #4f8cff; color: #f7fbff; border: none;
                border-radius: 12px; padding: 10px 12px; font-size: 14px; font-weight: 700;
            }
            QPushButton#action:hover { background: #6da0ff; }
            QPushButton#action:pressed { background: #3f79e8; }
            QPushButton#settings {
                background: #1b2838; color: #d7e4f1; border: 1px solid #355070;
                border-radius: 10px; padding: 4px 10px; font-size: 12px; font-weight: 600;
            }
            QPushButton#settings:hover { background: #26364b; }
            QProgressBar#progress {
                border: 1px solid #2d3f53; border-radius: 3px; background: #0f1824;
            }
            QProgressBar#progress::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4fd1ff, stop:1 #7effb2);
                border-radius: 3px;
            }
            """
        )
        self._apply_status("loading", "Cargando motor...")

    def _setup_animations(self):
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(350)
        self.status_timer.timeout.connect(self._tick_status)

        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(220)
        self.fade_in.setStartValue(0.94)
        self.fade_in.setEndValue(1.0)
        self.setWindowOpacity(0.94)
        self.fade_in.start()

    def _tick_status(self):
        if self.current_status not in {"loading", "processing", "refining"}:
            return
        self._dots = (self._dots + 1) % 4
        self.status.setText(f"{self.status_base_text}{'.' * self._dots}")

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
                "diagnostic_mode": False,
            },
            "dictionary": {},
        }

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

    def _load_app_settings(self):
        cfg = self._safe_load_config()
        app_cfg = cfg.setdefault("app", {})
        app_cfg.setdefault("hotkey", "ctrl+alt+s")
        app_cfg.setdefault("history_limit", 5)
        app_cfg.setdefault("timing_log_max_kb", 512)
        app_cfg.setdefault("diagnostic_mode", False)
        cfg["app"] = app_cfg
        self._save_config(cfg)
        self.history = self._load_history(app_cfg["history_limit"])
        return app_cfg

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
        if not self.app_config.get("diagnostic_mode", False):
            return
        payload["ts"] = datetime.now().isoformat(timespec="seconds")
        self._rotate_timing_log_if_needed()
        try:
            with open(self.timing_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"No se pudo escribir timing log: {e}")

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

    def _start_hotkey_listener(self):
        hotkey_value = self._normalize_hotkey(self.app_config.get("hotkey", "ctrl+alt+s"))
        self.app_config["hotkey"] = hotkey_value
        self.signals.hotkey_changed.emit(self._hotkey_to_label(hotkey_value))
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({self._hotkey_to_pynput(hotkey_value): self.toggle_dictation})
            self.hotkey_listener.start()
        except Exception as e:
            self.hotkey_listener = None
            self.signals.status_changed.emit("error", f"Hotkey invalida: {e}")

    def _restart_hotkey_listener(self):
        if self.hotkey_listener is not None:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        self._start_hotkey_listener()

    def open_settings(self):
        cfg = self._safe_load_config()
        old_model = str(cfg.get("engine", {}).get("model_size", "large-v3-turbo"))
        dlg = SettingsDialog(cfg, self.history, self.timing_log_path, self)
        if dlg.exec() != QDialog.Accepted:
            return

        new_cfg = dlg.result_config()
        new_cfg["app"]["hotkey"] = self._normalize_hotkey(new_cfg["app"].get("hotkey", "ctrl+alt+s"))
        self._save_config(new_cfg)
        self.app_config = new_cfg["app"]
        self.history = self._load_history(int(self.app_config.get("history_limit", 5)))
        self._restart_hotkey_listener()

        new_model = str(new_cfg.get("engine", {}).get("model_size", "large-v3-turbo"))
        if self.engine is not None:
            if old_model != new_model:
                threading.Thread(target=self._load_engine, daemon=True).start()
            else:
                self.engine.load_config(force=True)
        self.signals.status_changed.emit("idle", "Configuracion aplicada")

    def _load_engine(self):
        self.signals.status_changed.emit("loading", "Cargando motor...")
        try:
            self.engine = STTEngine()
            self.signals.status_changed.emit("idle", "Listo para dictar")
        except Exception as e:
            self.engine = None
            self.signals.status_changed.emit("error", f"Error cargando motor: {e}")

    def toggle_dictation(self):
        if self.is_processing:
            return
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.engine is None:
            self.signals.status_changed.emit("loading", "Motor aun no disponible")
            return
        if self.recorder.start_recording():
            self.is_recording = True
            self.signals.status_changed.emit("recording", "Escuchando...")

    def stop_recording(self):
        self.is_recording = False
        self.is_processing = True
        self.signals.status_changed.emit("processing", "Procesando audio...")
        audio_file = self.recorder.stop_recording()
        if not audio_file:
            self.is_processing = False
            self.signals.status_changed.emit("idle", "Listo para dictar")
            return
        threading.Thread(target=self.process_audio, args=(audio_file,), daemon=True).start()

    def process_audio(self, audio_file):
        t0 = time.perf_counter()
        transcribe_ms = 0.0
        paste_ms = 0.0
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
            self.signals.status_changed.emit("error", f"Error dictado: {e}")
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
            if not refine_started:
                self.signals.status_changed.emit("idle", "Listo para dictar")

    def refine_and_replace(self, original_text):
        self.signals.status_changed.emit("refining", "Refinando texto con IA...")
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
            self.signals.status_changed.emit("idle", "Listo para dictar")

    def _set_hotkey_text(self, hotkey_label):
        self.hint.setText(f"Hotkey: {hotkey_label}")

    def _apply_status(self, status, message):
        self.current_status = status
        self.status_base_text = message.rstrip(".")
        self._dots = 0
        self.status.setText(message)
        if status == "idle":
            self.mode.setText("IDLE")
            self.mode.setStyleSheet(
                "background:#1c2838;color:#b8c9dc;border:1px solid #364a62;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Iniciar dictado")
            self.progress.setVisible(False)
            self.status_timer.stop()
        elif status == "recording":
            self.mode.setText("REC")
            self.mode.setStyleSheet(
                "background:#3a1520;color:#ffd6de;border:1px solid #8d3a53;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Detener dictado")
            self.progress.setVisible(False)
            self.status_timer.stop()
        elif status == "processing":
            self.mode.setText("PROC")
            self.mode.setStyleSheet(
                "background:#2a3317;color:#dcf5bf;border:1px solid #607a35;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Procesando...")
            self.progress.setVisible(True)
            self.status_timer.start()
        elif status == "refining":
            self.mode.setText("AI")
            self.mode.setStyleSheet(
                "background:#2b1f40;color:#e9d3ff;border:1px solid #6e53a8;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Refinando...")
            self.progress.setVisible(True)
            self.status_timer.start()
        elif status == "loading":
            self.mode.setText("LOAD")
            self.mode.setStyleSheet(
                "background:#1f2b3c;color:#d0e8ff;border:1px solid #4b6b8f;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Cargando...")
            self.progress.setVisible(True)
            self.status_timer.start()
        else:
            self.mode.setText("ERR")
            self.mode.setStyleSheet(
                "background:#35171b;color:#ffd3d8;border:1px solid #8a3d48;border-radius:10px;padding:3px 10px;font-weight:700;"
            )
            self.action_btn.setText("Reintentar")
            self.progress.setVisible(False)
            self.status_timer.stop()

    def closeEvent(self, event):
        try:
            self.status_timer.stop()
        except Exception:
            pass
        try:
            if self.hotkey_listener is not None:
                self.hotkey_listener.stop()
        except Exception:
            pass
        try:
            self.recorder.cleanup()
        except Exception:
            pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = VoiceStallQtApp()
    win.show()
    sys.exit(app.exec())
