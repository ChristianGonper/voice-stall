import json
from unittest.mock import MagicMock, patch

import pytest

from engine import STTEngine


@pytest.fixture
def mock_whisper(mocker):
    return mocker.patch("engine.WhisperModel")


def test_engine_init(mock_whisper, mocker):
    mocker.patch("torch.cuda.is_available", return_value=True)
    engine = STTEngine()
    assert engine.model_size == "large-v3-turbo"
    mock_whisper.assert_called_once()


def test_apply_dictionary_is_pure_text_transform():
    with patch("engine.WhisperModel"):
        engine = STTEngine()
        engine.dictionary = {"paifón": "Python", "kiwin": "Qwen"}
        engine._dictionary_patterns = engine._build_dictionary_patterns(engine.dictionary)

        assert engine.apply_dictionary("Amo paifón") == "Amo Python"
        assert engine.apply_dictionary("El modelo kiwin es bueno") == "El modelo Qwen es bueno"
        assert engine.apply_dictionary("Nada que cambiar") == "Nada que cambiar"


def test_transcribe_returns_result(mock_whisper, mocker, tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_text("dummy audio")

    mock_segment = MagicMock()
    mock_segment.text = "Hola mundo"
    mock_whisper.return_value.transcribe.return_value = ([mock_segment], MagicMock())

    def side_effect(self, *args, **kwargs):
        self.config = {
            "engine": {
                "model_size": "large-v3-turbo",
                "compute_type": "float16",
                "profile": "balanced",
            }
        }
        self.model_size = "large-v3-turbo"
        self.language = "es"
        self.initial_prompt = "test"
        self.dictionary = {"hola mundo": "saludo"}
        self.profile = "balanced"
        self._dictionary_patterns = self._build_dictionary_patterns(self.dictionary)

    mocker.patch("engine.STTEngine.load_config", autospec=True, side_effect=side_effect)

    engine = STTEngine()
    result = engine.transcribe(str(audio_file))

    assert result.text == "saludo"
    assert result.raw_text == "Hola mundo"
    assert result.language == "es"


def test_load_config_falls_back_to_config_default(tmp_path, mocker):
    with patch("engine.WhisperModel"):
        mocker.patch("torch.cuda.is_available", return_value=True)
        engine = STTEngine()

    default_cfg = {
        "engine": {
            "model_size": "base",
            "language": "en",
            "compute_type": "float16",
            "initial_prompt": "Default prompt",
            "profile": "fast",
        },
        "dictionary": {"paifon": "Python"},
    }
    default_path = tmp_path / "config.default.json"
    default_path.write_text(json.dumps(default_cfg), encoding="utf-8")

    engine.config_path = str(tmp_path / "config.json")
    engine.default_config_path = str(default_path)
    engine.load_config(force=True)

    assert engine.model_size == "base"
    assert engine.language == "en"
    assert engine.profile == "fast"
    assert engine.dictionary == {"paifon": "Python"}
