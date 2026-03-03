from __future__ import annotations

from dataclasses import dataclass, field

from .SubtitleStyle import SubtitleStyle
from ..types import Color


@dataclass
class HighlightStyle(SubtitleStyle):

    highlight_color: Color = field(default_factory=lambda: (255, 215, 0))
    zoom_scale: float = 1.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.zoom_scale <= 0:
            raise ValueError(f"zoom_scale must be positive, got {self.zoom_scale}")
