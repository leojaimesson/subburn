from __future__ import annotations

from abc import ABC, abstractmethod

import av

from ..models.SubtitleSegment import SubtitleSegment
from ..options.SubtitleStyle import SubtitleStyle


class SubtitleRenderer(ABC):

    @abstractmethod
    def render(
        self,
        frame: av.VideoFrame,
        segment: SubtitleSegment,
        current_time: float,
        style: SubtitleStyle,
    ) -> av.VideoFrame:
        ...