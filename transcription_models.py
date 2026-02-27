from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    raw_text: str
    language: str
    timings: Dict[str, float] = field(default_factory=dict)
