"""Adapter for OpenAI Whisper transcription output.

Whisper returns a dict with the following relevant structure::

    {
        "text": "...",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 3.5,
                "text": " Hello world",
                "words": [                          # only present with word_timestamps=True
                    {"word": " Hello", "start": 0.0, "end": 1.2, "probability": 0.98},
                    {"word": " world", "start": 1.2, "end": 3.5, "probability": 0.95},
                ]
            },
            ...
        ]
    }

Word-level timestamps are available when transcribing with::

    model.transcribe(audio, word_timestamps=True)
"""
from __future__ import annotations

from typing import List

from ..models.SubtitleSegment import SubtitleSegment
from ..models.WordSegment import WordSegment


class WhisperAdapter:

    def __init__(self, result: dict) -> None:
        self._result = result

    def get_segments(self) -> List[SubtitleSegment]:
        segments: List[SubtitleSegment] = []

        for seg in self._result.get("segments", []):
            words = [
                WordSegment(
                    word=w["word"].strip(),
                    start=float(w["start"]),
                    end=float(w["end"]),
                )
                for w in seg.get("words", [])
            ]

            segments.append(
                SubtitleSegment(
                    start=float(seg["start"]),
                    end=float(seg["end"]),
                    text=seg["text"].strip(),
                    words=words,
                )
            )

        return segments
