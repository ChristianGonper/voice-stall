# Voice Stall - Tech Stack

## Programming Languages
- **Python (>=3.12)**: The primary engine for speech-to-text, audio recording, and system automation.
- **TypeScript**: Used for building a robust and type-safe frontend within the Tauri app.
- **Rust**: Used for the Tauri application shell, managing the windowing and sidecar processes.

## Application Architecture
- **Tauri + React**: A modern, lightweight framework for the desktop shell and the user interface.
- **Python Sidecar**: A persistent backend service that performs the compute-intensive transcription and automation tasks, communicating via JSON over standard input/output.

## Core Libraries & Engines
- **STT Engine**: `faster-whisper` (>=1.2.1) - A high-performance reimplementation of OpenAI's Whisper model.
- **Execution**: `torch` (2.5.1) with NVIDIA CUDA 12.1 support for GPU-accelerated transcription on Windows.
- **Audio Capture**: `pyaudio` - Real-time audio recording from the system's microphone.
- **Automation & Hotkeys**: `pyautogui`, `pynput`, and `pyperclip` for global hotkey management and automatic text pasting.
- **Tauri Plugins**: `@tauri-apps/plugin-clipboard-manager` for secure and robust clipboard access.

## Development & Testing
- **Package Management**: `uv` - A fast Python package installer and resolver.
- **Testing**: 
  - `pytest` for unit tests and automated verification of the Python engine.
  - `vitest` and `@testing-library/react` for comprehensive frontend component and style testing.
- **Frontend Tooling**: `npm` for managing React and Tauri dependencies.
- **Build System**: Tauri CLI for building the production-ready Windows installer.
