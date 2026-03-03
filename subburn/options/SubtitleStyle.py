from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from ..enums.TextAlign import TextAlign
from ..enums.TextCase import TextCase
from ..enums.Position import Position
from ..types import BoxShadow, Color


@dataclass
class SubtitleStyle:

    font_path: Optional[str] = None
    font_size: int = 48
    position: Position = Position.BOTTOM_CENTER
    padding: int = 40
    max_width_ratio: float = 0.9
    line_spacing: int = 6
    color: Color = field(default_factory=lambda: (255, 255, 255))
    stroke_color: Optional[Color] = None
    stroke_width: int = 1
    box_shadow: Optional[Union[BoxShadow, List[BoxShadow]]] = None
    text_case: TextCase = TextCase.NORMAL
    text_align: TextAlign = TextAlign.CENTER

    def __post_init__(self) -> None:
        if not (0.0 < self.max_width_ratio <= 1.0):
            raise ValueError(
                f"max_width_ratio must be between 0 and 1, got {self.max_width_ratio}"
            )
        if self.font_size <= 0:
            raise ValueError(f"font_size must be positive, got {self.font_size}")
        if self.padding < 0:
            raise ValueError(f"padding must be >= 0, got {self.padding}")
        if self.stroke_width < 0:
            raise ValueError(f"stroke_width must be >= 0, got {self.stroke_width}")
        if isinstance(self.position, str):
            object.__setattr__(self, "position", Position(self.position))
