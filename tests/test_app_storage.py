import json

from app_storage import AppStorage


def test_load_config_merges_defaults(tmp_path):
    storage = AppStorage(str(tmp_path))
    cfg = {"app": {"hotkey": "ctrl+shift+s"}, "dictionary": {"foo": "bar"}}
    (tmp_path / "config.default.json").write_text(json.dumps(cfg), encoding="utf-8")

    loaded = storage.load_config()

    assert loaded["config_version"] == 1
    assert loaded["app"]["hotkey"] == "ctrl+shift+s"
    assert loaded["app"]["history_limit"] == 5
    assert loaded["dictionary"] == {"foo": "bar"}


def test_load_app_settings_persists_config_json(tmp_path):
    storage = AppStorage(str(tmp_path))
    app_cfg = storage.load_app_settings()

    assert app_cfg["hotkey"] == "ctrl+alt+s"
    assert (tmp_path / "config.json").exists()


def test_push_history_applies_limit_and_saves(tmp_path):
    storage = AppStorage(str(tmp_path))
    history = [{"ts": "2026-01-01T00:00:00", "text": "old"}]

    updated = storage.push_history(history, "new", history_limit=1)

    assert len(updated) == 1
    assert updated[0]["text"] == "new"
    saved = json.loads((tmp_path / "dictation_history.json").read_text(encoding="utf-8"))
    assert saved[0]["text"] == "new"


def test_log_timing_writes_when_enabled(tmp_path):
    storage = AppStorage(str(tmp_path))

    storage.log_timing({"event": "dictation_cycle", "total_ms": 123.0}, diagnostic_mode=True, max_kb=512)

    data = (tmp_path / "timings.log").read_text(encoding="utf-8").strip().splitlines()
    assert len(data) == 1
    row = json.loads(data[0])
    assert row["event"] == "dictation_cycle"
    assert "ts" in row


def test_log_timing_rotates_when_exceeds_limit(tmp_path):
    storage = AppStorage(str(tmp_path))
    timing_path = tmp_path / "timings.log"
    timing_path.write_text("x" * 2048, encoding="utf-8")

    storage.log_timing({"event": "dictation_cycle", "total_ms": 5.0}, diagnostic_mode=True, max_kb=1)

    assert (tmp_path / "timings.log.1").exists()
    current = (tmp_path / "timings.log").read_text(encoding="utf-8")
    assert "dictation_cycle" in current
