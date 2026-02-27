import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dictation_service import DictationService
from engine import STTEngine
from transcription_models import TranscriptionResult


class FakeEngine:
    def __init__(self, text="texto de prueba"):
        self._result = TranscriptionResult(text=text, raw_text=text, language="es")

    def transcribe(self, _audio_file):
        return self._result


def _stats(values):
    if not values:
        return {"n": 0, "mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}
    ordered = sorted(values)
    p95_idx = int(0.95 * (len(ordered) - 1))
    return {
        "n": len(values),
        "mean_ms": round(statistics.fmean(values), 3),
        "median_ms": round(statistics.median(values), 3),
        "p95_ms": round(ordered[p95_idx], 3),
        "min_ms": round(ordered[0], 3),
        "max_ms": round(ordered[-1], 3),
    }


def benchmark_dictation_service(iterations):
    service = DictationService(FakeEngine())
    values = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _cycle = service.transcribe("dummy.wav")
        values.append((time.perf_counter() - t0) * 1000)
    return _stats(values)


def benchmark_dictionary_apply(iterations):
    engine = STTEngine.__new__(STTEngine)
    engine.dictionary = {
        "paifon": "Python",
        "matlap": "Matlab",
        "kiwin": "Qwen",
        "voz tal": "Voice Stall",
        "geminiclip": "gemini-cli",
    }
    engine._dictionary_patterns = STTEngine._build_dictionary_patterns(engine, engine.dictionary)
    phrase = "hola paifon y matlap con kiwin en voz tal y geminiclip"
    values = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = STTEngine.apply_dictionary(engine, phrase)
        values.append((time.perf_counter() - t0) * 1000)
    return _stats(values)


def benchmark_engine_transcribe(audio_path, runs):
    engine = STTEngine()
    values = []
    for _ in range(runs):
        t0 = time.perf_counter()
        _ = engine.transcribe(audio_path)
        values.append((time.perf_counter() - t0) * 1000)
    return _stats(values)


def write_markdown(path, payload):
    lines = [
        "# Benchmark Report",
        "",
        f"- Timestamp: `{payload['timestamp']}`",
        f"- Iterations: `{payload['iterations']}`",
        "",
        "## Dictation Service (orchestrator overhead)",
        f"- Mean: `{payload['dictation_service']['mean_ms']} ms`",
        f"- Median: `{payload['dictation_service']['median_ms']} ms`",
        f"- P95: `{payload['dictation_service']['p95_ms']} ms`",
        "",
        "## Dictionary Apply",
        f"- Mean: `{payload['dictionary_apply']['mean_ms']} ms`",
        f"- Median: `{payload['dictionary_apply']['median_ms']} ms`",
        f"- P95: `{payload['dictionary_apply']['p95_ms']} ms`",
    ]
    if payload.get("engine_transcribe"):
        lines.extend(
            [
                "",
                "## Engine Transcribe (real audio)",
                f"- Mean: `{payload['engine_transcribe']['mean_ms']} ms`",
                f"- Median: `{payload['engine_transcribe']['median_ms']} ms`",
                f"- P95: `{payload['engine_transcribe']['p95_ms']} ms`",
            ]
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- `dictation_service` should stay near-zero; any growth indicates orchestration regressions.",
            "- `dictionary_apply` should remain sub-millisecond; growth suggests regex bloat.",
            "- Compare this file across commits for trend tracking.",
        ]
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run local benchmarks for Voice Stall.")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--audio", type=str, default="")
    parser.add_argument("--audio-runs", type=int, default=5)
    parser.add_argument("--out-dir", type=str, default="benchmarks")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "iterations": args.iterations,
        "dictation_service": benchmark_dictation_service(args.iterations),
        "dictionary_apply": benchmark_dictionary_apply(args.iterations),
    }
    if args.audio:
        payload["engine_transcribe"] = benchmark_engine_transcribe(args.audio, args.audio_runs)

    json_path = os.path.join(args.out_dir, "benchmark_latest.json")
    md_path = os.path.join(args.out_dir, "benchmark_latest.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    write_markdown(md_path, payload)
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
