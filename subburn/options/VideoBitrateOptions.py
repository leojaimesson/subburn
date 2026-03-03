from __future__ import annotations

import re
from dataclasses import dataclass

_BITRATE_RE = re.compile(r"^\d+(\.\d+)?[KkMmGg]?$")


def _validate_bitrate_str(name: str, value: str) -> None:
    if not _BITRATE_RE.match(value):
        raise ValueError(
            f"{name} must be a valid FFmpeg bitrate string (e.g. '2M', '500k'), "
            f"got {value!r}"
        )


@dataclass
class VideoBitrateOptions:

    auto_bitrate: bool = True
    video_bitrate: str | None = None
    maxrate: str | None = None
    bufsize: str | None = None
    cq: int | None = None

    def __post_init__(self) -> None:
        if self.cq is not None and not (0 <= self.cq <= 51):
            raise ValueError(f"cq must be between 0 and 51, got {self.cq}")
        for field_name, value in (
            ("video_bitrate", self.video_bitrate),
            ("maxrate", self.maxrate),
            ("bufsize", self.bufsize),
        ):
            if value is not None:
                _validate_bitrate_str(field_name, value)
