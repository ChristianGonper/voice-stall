import time
from unittest.mock import MagicMock
import python_backend
from python_backend import SidecarServer

def test_hotkey_trigger_verification(tmp_path):
    """
    Verifica que el trigger del hotkey sea robusto ante estados inconsistentes.
    """
    server = SidecarServer.__new__(SidecarServer)
    server.last_trigger_time = 0
    server.is_processing = False
    server.is_pasting = False
    server.app_cfg = {"hotkey": "ctrl+alt+s"}
    server.key_press_times = {"s": time.monotonic()}
    server.toggle_dictation = MagicMock()
    server._emit_status = MagicMock()

    # Escenario 1: Disparo normal
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 1

    # Escenario 2: Debounce (disparo demasiado rápido)
    server.last_trigger_time = time.time()
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 1 # No debe haber aumentado

    # Escenario 3: Bloqueo por procesamiento
    server.last_trigger_time = 0
    server.is_processing = True
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 1 # No debe haber aumentado


def test_hotkey_requires_final_key_pressed(monkeypatch):
    server = SidecarServer.__new__(SidecarServer)
    server.last_trigger_time = 0
    server.is_processing = False
    server.is_pasting = False
    server.app_cfg = {"hotkey": "ctrl+alt+s"}
    server.key_press_times = {}
    server.toggle_dictation = MagicMock()
    server._emit_status = MagicMock()

    dummy_keyboard = type(
        "DummyKeyboard",
        (),
        {
            "Key": type(
                "DummyKey",
                (),
                {
                    "ctrl": "ctrl",
                    "ctrl_l": "ctrl_l",
                    "ctrl_r": "ctrl_r",
                    "alt": "alt",
                    "alt_l": "alt_l",
                    "alt_r": "alt_r",
                    "shift": "shift",
                    "shift_l": "shift_l",
                    "shift_r": "shift_r",
                    "cmd": "cmd",
                    "cmd_l": "cmd_l",
                    "cmd_r": "cmd_r",
                },
            ),
            "KeyCode": type(
                "DummyKeyCode",
                (),
                {"from_char": staticmethod(lambda char: f"char:{char}")},
            ),
        },
    )
    monkeypatch.setattr(python_backend, "keyboard", dummy_keyboard)

    server.pressed_keys = {17, 18}
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 0

    server.last_trigger_time = 0
    server.pressed_keys = {17, 18, ord("S")}
    server.key_press_times = {"s": time.monotonic()}
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 1


def test_hotkey_rejects_stale_final_key(monkeypatch):
    server = SidecarServer.__new__(SidecarServer)
    server.last_trigger_time = 0
    server.is_processing = False
    server.is_pasting = False
    server.app_cfg = {"hotkey": "ctrl+alt+s"}
    server.key_press_times = {"s": time.monotonic() - 2}
    server.toggle_dictation = MagicMock()
    server._emit_status = MagicMock()

    dummy_keyboard = type(
        "DummyKeyboard",
        (),
        {
            "Key": type(
                "DummyKey",
                (),
                {
                    "ctrl": "ctrl",
                    "ctrl_l": "ctrl_l",
                    "ctrl_r": "ctrl_r",
                    "alt": "alt",
                    "alt_l": "alt_l",
                    "alt_r": "alt_r",
                },
            ),
            "KeyCode": type(
                "DummyKeyCode",
                (),
                {"from_char": staticmethod(lambda char: f"char:{char}")},
            ),
        },
    )
    monkeypatch.setattr(python_backend, "keyboard", dummy_keyboard)

    server.pressed_keys = {17, 18, ord("S")}
    server._on_hotkey_trigger()
    assert server.toggle_dictation.call_count == 0
