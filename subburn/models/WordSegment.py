from dataclasses import dataclass


@dataclass(frozen=True)
class WordSegment:
    word: str
    start: float
    end: float
