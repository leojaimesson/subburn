from __future__ import annotations

from typing import Dict, Tuple

import av
import numpy as np
from PIL import Image, ImageDraw

from .base import SubtitleRenderer
from ..enums.TextCase import TextCase
from ..models.SubtitleSegment import SubtitleSegment
from ..options.SubtitleStyle import SubtitleStyle
from ..utils.text import (
    circle_offsets,
    compute_block_position,
    line_x_offset,
    load_font,
    normalize_box_shadows,
    split_color_and_opacity,
    wrap_text,
)

_OverlayCacheKey = Tuple[float, float, str, int, int]


class StandardRenderer(SubtitleRenderer):

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

        cache_key: _OverlayCacheKey = (
            segment.start, segment.end, segment.text, width, height
        )
        overlay = self._overlay_cache.get(cache_key)
        if overlay is None:
            overlay = self._build_overlay(segment, style, width, height)
            self._overlay_cache[cache_key] = overlay

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        return av.VideoFrame.from_ndarray(np.asarray(composed), format="rgb24")

    def _build_overlay(
        self,
        segment: SubtitleSegment,
        style: SubtitleStyle,
        width: int,
        height: int,
    ) -> Image.Image:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font = load_font(style)
        stroke_width = max(0, int(style.stroke_width or 0))
        shadows = normalize_box_shadows(style)
        text_color, text_opacity = split_color_and_opacity(style.color)
        stroke_color, stroke_opacity = split_color_and_opacity(style.stroke_color)

        text = _apply_text_case(segment.text, style)
        max_line_width = int(width * style.max_width_ratio) - style.padding * 2
        lines = wrap_text(text, draw, font, max_line_width)

        line_height = font.getbbox("Ay")[3] + style.line_spacing
        block_height = line_height * len(lines)
        block_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)

        block_x, block_y = compute_block_position(width, height, block_width, block_height, style)

        cursor_y = block_y
        for line in lines:
            line_width = draw.textbbox((0, 0), line, font=font)[2]
            cursor_x = line_x_offset(block_x, block_width, line_width, style.text_align)

            _draw_shadows(draw, line, font, cursor_x, cursor_y, shadows)

            if stroke_width > 0:
                draw.text(
                    (cursor_x, cursor_y),
                    line,
                    font=font,
                    fill=(*text_color, text_opacity),
                    stroke_width=stroke_width,
                    stroke_fill=(*stroke_color, stroke_opacity),
                )
            else:
                draw.text(
                    (cursor_x, cursor_y),
                    line,
                    font=font,
                    fill=(*text_color, text_opacity),
                )

            cursor_y += line_height

        return overlay


def _apply_text_case(text: str, style: SubtitleStyle) -> str:
    if style.text_case == TextCase.UPPER:
        return text.upper()
    if style.text_case == TextCase.LOWER:
        return text.lower()
    return text


def _draw_shadows(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    x: int,
    y: int,
    shadows: list,
) -> None:
    for shadow in shadows:
        offset_x, offset_y = shadow["offset"]
        for blur_dx, blur_dy in circle_offsets(shadow["blur"]):
            draw.text(
                (x + offset_x + blur_dx, y + offset_y + blur_dy),
                text,
                font=font,
                fill=(*shadow["color"], shadow["opacity"]),
            )
