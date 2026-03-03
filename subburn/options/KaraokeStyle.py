from __future__ import annotations

from dataclasses import dataclass, field

from .SubtitleStyle import SubtitleStyle
from ..types import Color


@dataclass
class KaraokeStyle(SubtitleStyle):

    spoken_color: Color = field(default_factory=lambda: (255, 215, 0))

    def __post_init__(self) -> None:
        super().__post_init__()
