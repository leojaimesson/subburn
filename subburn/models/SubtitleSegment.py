from dataclasses import dataclass
from typing import List
from .WordSegment import WordSegment


@dataclass(frozen=True)
class SubtitleSegment:
    start: float
    end: float
    text: str
    words: List[WordSegment]
