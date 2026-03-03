from __future__ import annotations

from typing import Dict, List, Tuple

import av
import numpy as np
from PIL import Image, ImageDraw

from .base import SubtitleRenderer
from .standard import _apply_text_case, _draw_shadows
from ..models.SubtitleSegment import SubtitleSegment
from ..models.WordSegment import WordSegment
from ..options.SubtitleStyle import SubtitleStyle
from ..utils.text import (
    compute_block_position,
    line_x_offset,
    load_font,
    normalize_box_shadows,
    split_color_and_opacity,
    wrap_text,
)

_DEFAULT_SPOKEN_COLOR = (255, 215, 0)

_OverlayCacheKey = Tuple[float, float, str, int, int, int]


class KaraokeRenderer(SubtitleRenderer):

    def __init__(self) -> None:
        self._overlay_cache: Dict[_OverlayCacheKey, Image.Image] = {}

    def render(
        self,
        frame: av.VideoFrame,
        segment: SubtitleSegment,
        current_time: float,
        style: SubtitleStyle,
    ) -> av.VideoFrame:
        base = Image.fromarray(frame.to_ndarray(format="rgb24")).convert("RGBA")
        width, height = base.size

        words: List[WordSegment] = segment.words or []
        spoken_count = _count_spoken_words(words, current_time)

        cache_key: _OverlayCacheKey = (
            segment.start, segment.end, segment.text,
            spoken_count, width, height,
        )
        overlay = self._overlay_cache.get(cache_key)
        if overlay is None:
            overlay = self._build_overlay(
                segment, words, spoken_count, style, width, height
            )
            self._overlay_cache[cache_key] = overlay

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        return av.VideoFrame.from_ndarray(np.asarray(composed), format="rgb24")

    def _build_overlay(
        self,
        segment: SubtitleSegment,
        words: List[WordSegment],
        spoken_count: int,
        style: SubtitleStyle,
        width: int,
        height: int,
    ) -> Image.Image:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font = load_font(style)
        stroke_width = max(0, int(style.stroke_width or 0))
        shadows = normalize_box_shadows(style)

        base_color, base_opacity = split_color_and_opacity(style.color)
        spoken_color, spoken_opacity = split_color_and_opacity(
            getattr(style, "spoken_color", _DEFAULT_SPOKEN_COLOR)
        )
        stroke_color, stroke_opacity = split_color_and_opacity(style.stroke_color)

        text = _apply_text_case(segment.text, style)
        max_line_width = int(width * style.max_width_ratio) - style.padding * 2
        lines = wrap_text(text, draw, font, max_line_width)

        line_height = font.getbbox("Ay")[3] + style.line_spacing
        block_height = line_height * len(lines)
        block_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)
        block_x, block_y = compute_block_position(width, height, block_width, block_height, style)

        word_counter = 0
        cursor_y = block_y

        for line in lines:
            line_words = line.split()
            line_width = sum(
                draw.textbbox((0, 0), w + " ", font=font)[2] for w in line_words
            )
            cursor_x = line_x_offset(block_x, block_width, line_width, style.text_align)

            for word in line_words:
                is_spoken = word_counter < spoken_count
                fill_color = spoken_color if is_spoken else base_color
                fill_opacity = spoken_opacity if is_spoken else base_opacity

                token = word + " "

                _draw_shadows(draw, token, font, cursor_x, cursor_y, shadows)

                if stroke_width > 0:
                    draw.text(
                        (cursor_x, cursor_y),
                        token,
                        font=font,
                        fill=(*fill_color, fill_opacity),
                        stroke_width=stroke_width,
                        stroke_fill=(*stroke_color, stroke_opacity),
                    )
                else:
                    draw.text(
                        (cursor_x, cursor_y),
                        token,
                        font=font,
                        fill=(*fill_color, fill_opacity),
                    )

                cursor_x += draw.textbbox((0, 0), token, font=font)[2]
                word_counter += 1

            cursor_y += line_height

        return overlay


def _count_spoken_words(words: List[WordSegment], current_time: float) -> int:
    return sum(1 for word in words if word.end <= current_time)
