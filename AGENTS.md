# Repository Guidelines

## Project Structure & Module Organization
Core application code lives at the repository root:
- `main_qt.py`: PySide6 UI, hotkey handling, app state, and dictation flow.
- `engine.py`: speech-to-text engine (`faster-whisper`), profile settings, and dictionary replacements.
- `recorder.py`: audio capture and temporary WAV handling.

Tests are under `tests/` (for example `tests/test_engine.py`, `tests/test_recorder.py`). Runtime/config artifacts include `config.json`, `dictation_history.json`, and `timings.log`. Keep new modules focused and place unit tests in `tests/` with matching names (for example `foo.py` -> `tests/test_foo.py`).

## Build, Test, and Development Commands
- `uv sync`: install project and dev dependencies from `pyproject.toml`/`uv.lock`.
- `uv run main_qt.py`: run the app locally.
- `uv run main_qt.py --diag`: run with diagnostic metrics enabled.
- `uv run pytest -q`: run the full test suite quietly.

Use Python 3.12+ (see `.python-version` and `pyproject.toml`).

## Coding Style & Naming Conventions
Follow Python conventions:
- 4-space indentation, UTF-8 files, and clear function boundaries.
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Keep UI logic in `main_qt.py` and STT/transcription logic in `engine.py`; avoid cross-file coupling.

No dedicated formatter/linter is currently configured in this repo. Keep code PEP 8-aligned and keep imports and side effects explicit.

## Testing Guidelines
Framework: `pytest` with `pytest-mock`.
- Name tests `test_*` and keep one behavior per test.
- Mock heavy/runtime dependencies (`WhisperModel`, network calls, CUDA availability) to keep tests deterministic.
- Add tests for all behavior changes, especially config loading, dictionary transformations, and error fallbacks.

Run `uv run pytest -q` before opening a PR.

## Commit & Pull Request Guidelines
Recent history uses conventional prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `release:`. Keep commit messages short, imperative, and scoped to one change.

PRs should include:
- What changed and why.
- User-visible impact (UI, hotkeys, config keys, diagnostics).
- Linked issue/task when applicable.
- Screenshots/GIFs for UI changes and test results (`uv run pytest -q`).
