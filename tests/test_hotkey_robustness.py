import time
import pytest
from unittest.mock import MagicMock, patch
from python_backend import SidecarServer

def test_hotkey_trigger_verification(tmp_path):
    """
    Verifica que el trigger del hotkey sea robusto ante estados inconsistentes.
    """
    server = SidecarServer.__new__(SidecarServer)
    server.last_trigger_time = 0
    server.is_processing = False
    server.is_pasting = False
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
