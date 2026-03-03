from __future__ import annotations

from typing import List, Optional

from ..models.SubtitleSegment import SubtitleSegment
from ..models.WordSegment import WordSegment


class WhisperXAdapter:

    def __init__(self, result: dict, *, include_speaker: bool = False) -> None:
        self._result = result
        self._include_speaker = include_speaker

    def get_segments(self) -> List[SubtitleSegment]:
        segments: List[SubtitleSegment] = []

        for seg in self._result.get("segments", []):
            words = self._parse_words(seg.get("words", []))
            text = seg.get("text", "").strip()

            if self._include_speaker:
                speaker: Optional[str] = seg.get("speaker")
                if speaker:
                    text = f"[{speaker}] {text}"

            segments.append(
                SubtitleSegment(
                    start=float(seg["start"]),
                    end=float(seg["end"]),
                    text=text,
                    words=words,
                )
            )

        return segments

    @staticmethod
    def _parse_words(raw_words: list) -> List[WordSegment]:
        result: List[WordSegment] = []
        for w in raw_words:
            start = w.get("start")
            end = w.get("end")
            if start is None or end is None:
                continue
            result.append(
                WordSegment(
                    word=w["word"].strip(),
                    start=float(start),
                    end=float(end),
                )
            )
        return result
