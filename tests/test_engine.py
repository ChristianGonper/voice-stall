import pytest
import json
import os
from unittest.mock import MagicMock, patch
from engine import STTEngine

@pytest.fixture
def mock_whisper(mocker):
    # Mock WhisperModel para evitar cargar el modelo real
    return mocker.patch("engine.WhisperModel")

@pytest.fixture
def mock_config(tmp_path):
    # Crear un archivo config.json temporal para los tests
    config_data = {
        "engine": {
            "model_size": "tiny",
            "language": "es",
            "compute_type": "float16",
            "initial_prompt": "Test prompt",
            "use_llm": False
        },
        "dictionary": {
            "test_word": "replaced_word",
            "hola mundo": "saludo"
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    return str(config_file)

def test_engine_init(mock_whisper, mocker):
    mocker.patch("torch.cuda.is_available", return_value=True)
    engine = STTEngine()
    assert engine.model_size == "large-v3-turbo"
    mock_whisper.assert_called_once()

def test_apply_dictionary():
    # Mockeamos la inicialización para no cargar el modelo
    with patch("engine.WhisperModel"):
        engine = STTEngine()
        engine.dictionary = {"paifón": "Python", "kiwin": "Qwen"}
        
        assert engine.apply_dictionary("Amo paifón") == "Amo Python"
        assert engine.apply_dictionary("El modelo kiwin es bueno") == "El modelo Qwen es bueno"
        assert engine.apply_dictionary("Nada que cambiar") == "Nada que cambiar"

def test_apply_dictionary_commands(mocker):
    # Test del comando "abre"
    with patch("engine.WhisperModel"):
        mock_web = mocker.patch("webbrowser.open")
        engine = STTEngine()
        
        result = engine.apply_dictionary("abre google")
        assert "Opening google" in result
        mock_web.assert_called_with("https://www.google.com")

def test_transcribe(mock_whisper, mocker, tmp_path):
    # Simular un archivo de audio existente
    audio_file = tmp_path / "test.wav"
    audio_file.write_text("dummy audio")
    
    # Mock de los segmentos devueltos por Whisper
    mock_segment = MagicMock()
    mock_segment.text = "Hola mundo"
    mock_whisper.return_value.transcribe.return_value = ([mock_segment], MagicMock())
    
    # Mockear load_config para que inicialice atributos básicos
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
        self.use_llm = False
        self.dictionary = {"hola mundo": "saludo"}
        self.profile = "balanced"
        self._dictionary_patterns = self._build_dictionary_patterns(self.dictionary)

    mocker.patch("engine.STTEngine.load_config", autospec=True, side_effect=side_effect)
    
    engine = STTEngine()
    # Aseguramos que los atributos estén ahí (aunque ya lo hace el side_effect)
    engine.dictionary = {"hola mundo": "saludo"}
    
    result = engine.transcribe(str(audio_file))
    assert result == "saludo"

def test_refine_with_llm(mocker):
    with patch("engine.WhisperModel"):
        engine = STTEngine()
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Texto Refinado"}
        
        result = engine.refine_with_llm("Texto original")
        assert result == "Texto Refinado"
        
def test_refine_with_llm_error(mocker):
    with patch("engine.WhisperModel"):
        engine = STTEngine()
        mock_post = mocker.patch("requests.post", side_effect=Exception("Connection Error"))
        
        # Debe devolver el texto original si falla el LLM
        result = engine.refine_with_llm("Texto original")
        assert result == "Texto original"
