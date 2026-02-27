import json
from pathlib import Path

from python_backend import SidecarServer


class DummyStorage:
    def __init__(self, log_path: Path):
        self.timing_log_path = str(log_path)


def make_server_without_init(tmp_path: Path):
    server = SidecarServer.__new__(SidecarServer)
    server.storage = DummyStorage(tmp_path / "timings.log")
    return server


def test_normalize_hotkey_variants(tmp_path):
    server = make_server_without_init(tmp_path)
    assert server._normalize_hotkey("Control + Option + S") == "ctrl+alt+s"
    assert server._normalize_hotkey("f8") == "ctrl+alt+s"


def test_compute_recent_metrics_reads_last_n(tmp_path):
    server = make_server_without_init(tmp_path)
    rows = [
        {"event": "dictation_cycle", "total_ms": 10, "transcribe_ms": 5, "paste_ms": 2},
        {"event": "dictation_cycle", "total_ms": 20, "transcribe_ms": 8, "paste_ms": 3},
        {"event": "other", "total_ms": 99, "transcribe_ms": 99, "paste_ms": 99},
    ]
    with open(server.storage.timing_log_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    result = server._compute_recent_metrics(last_n=2)
    assert result["count"] == 2
    assert result["avg_total_ms"] == 15
    assert result["avg_transcribe_ms"] == 6.5
    assert result["avg_paste_ms"] == 2.5


def test_handle_unknown_method_raises(tmp_path):
    server = make_server_without_init(tmp_path)
    try:
        server.handle("unknown", {})
    except ValueError as exc:
        assert "Metodo no soportado" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
