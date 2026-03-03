from __future__ import annotations

import re
from pathlib import Path
from typing import List, Union

from ..models.SubtitleSegment import SubtitleSegment


_TIMESTAMP_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})"
)


def _to_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


class SRTAdapter:

    def __init__(self, source: Union[str, Path]) -> None:
        path = Path(source)
        if path.exists():
            self._content = path.read_text(encoding="utf-8")
        else:
            self._content = str(source)

    def get_segments(self) -> List[SubtitleSegment]:
        segments: List[SubtitleSegment] = []
        blocks = re.split(r"\n\s*\n", self._content.strip())

        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) < 2:
                continue

            timestamp_line = None
            text_start = 1
            for i, line in enumerate(lines):
                if _TIMESTAMP_RE.search(line):
                    timestamp_line = line
                    text_start = i + 1
                    break

            if timestamp_line is None:
                continue

            match = _TIMESTAMP_RE.search(timestamp_line)
            if not match:
                continue

            start = _to_seconds(*match.group(1, 2, 3, 4))
            end = _to_seconds(*match.group(5, 6, 7, 8))
            text = " ".join(lines[text_start:]).strip()

            if not text:
                continue

            segments.append(
                SubtitleSegment(
                    start=start,
                    end=end,
                    text=text,
                    words=[],
                )
            )

        return segments
