from __future__ import annotations

import re
from pathlib import Path
from typing import List, Union

from ..models.SubtitleSegment import SubtitleSegment


# HH:MM:SS.mmm or MM:SS.mmm
_TIMESTAMP_RE = re.compile(
    r"(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{3})"
)

_SKIP_BLOCK_RE = re.compile(r"^(NOTE|STYLE|REGION)\b")


def _to_seconds(h: str | None, m: str, s: str, ms: str) -> float:
    return (int(h) if h else 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


class VTTAdapter:

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
            if not lines:
                continue

            if lines[0].startswith("WEBVTT") or _SKIP_BLOCK_RE.match(lines[0]):
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

            start = _to_seconds(match.group(1), match.group(2), match.group(3), match.group(4))
            end = _to_seconds(match.group(5), match.group(6), match.group(7), match.group(8))

            # Strip VTT cue settings (e.g. "align:center position:50%") from text
            text_lines = [
                re.sub(r"<[^>]+>", "", line).strip()  # remove inline tags like <00:00:01.000>
                for line in lines[text_start:]
            ]
            text = " ".join(t for t in text_lines if t)

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
