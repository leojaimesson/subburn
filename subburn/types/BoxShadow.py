from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .Color import Color


@dataclass(frozen=True)
class BoxShadow:

    color: Color = field(default=(0, 0, 0, 0.5))
    offset: Tuple[int, int] = (0, 0)
    blur: int = 0

    def __post_init__(self) -> None:
        if self.blur < 0:
            raise ValueError(f"BoxShadow.blur must be >= 0, got {self.blur}")
        if not isinstance(self.offset, (list, tuple)) or len(self.offset) != 2:
            raise ValueError("BoxShadow.offset must be a (x, y) tuple of two ints")
