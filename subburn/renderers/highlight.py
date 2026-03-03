from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import av
import numpy as np
from PIL import Image, ImageDraw

from .base import SubtitleRenderer
from .standard import _apply_text_case, _draw_shadows
from ..models.SubtitleSegment import SubtitleSegment
from ..models.WordSegment import WordSegment
from ..options.SubtitleStyle import SubtitleStyle
from ..utils.text import (
    circle_offsets,
    compute_block_position,
    line_x_offset,
    load_font,
    load_font_at_size,
    normalize_box_shadows,
    split_color_and_opacity,
    wrap_text,
)

_DEFAULT_HIGHLIGHT_COLOR = (255, 215, 0)
_DEFAULT_ZOOM_SCALE = 1.0

_OverlayCacheKey = Tuple[float, float, str, int, int, int]


class HighlightRenderer(SubtitleRenderer):

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
        active_word_index = _find_active_word_index(words, current_time)

        cache_key: _OverlayCacheKey = (
            segment.start, segment.end, segment.text,
            active_word_index, width, height,
        )
        overlay = self._overlay_cache.get(cache_key)
        if overlay is None:
            overlay = self._build_overlay(
                segment, words, active_word_index, style, width, height
            )
            self._overlay_cache[cache_key] = overlay

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        return av.VideoFrame.from_ndarray(np.asarray(composed), format="rgb24")

    def _build_overlay(
        self,
        segment: SubtitleSegment,
        words: List[WordSegment],
        active_word_index: int,
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
        highlight_color, highlight_opacity = split_color_and_opacity(
            getattr(style, "highlight_color", _DEFAULT_HIGHLIGHT_COLOR)
        )
        stroke_color, stroke_opacity = split_color_and_opacity(style.stroke_color)

        zoom_scale: float = getattr(style, "zoom_scale", _DEFAULT_ZOOM_SCALE)
        zoom_font: Optional[object] = None
        if zoom_scale != 1.0:
            zoom_font = load_font_at_size(style.font_path, int(style.font_size * zoom_scale))

        text = _apply_text_case(segment.text, style)
        max_line_width = int(width * style.max_width_ratio) - style.padding * 2
        lines = wrap_text(text, draw, font, max_line_width)

        line_height = font.getbbox("Ay")[3] + style.line_spacing
        if zoom_font:
            line_height = max(line_height, zoom_font.getbbox("Ay")[3] + style.line_spacing)

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
                is_active = word_counter == active_word_index
                glyph_font = zoom_font if (is_active and zoom_font) else font
                fill_color = highlight_color if is_active else base_color
                fill_opacity = highlight_opacity if is_active else base_opacity

                glyph_y = cursor_y
                if is_active and zoom_font:
                    normal_height = font.getbbox(word)[3]
                    zoomed_height = zoom_font.getbbox(word)[3]
                    glyph_y = cursor_y - (zoomed_height - normal_height)

                token = word + " "

                _draw_shadows(draw, token, glyph_font, cursor_x, glyph_y, shadows)

                if stroke_width > 0:
                    draw.text(
                        (cursor_x, glyph_y),
                        token,
                        font=glyph_font,
                        fill=(*fill_color, fill_opacity),
                        stroke_width=stroke_width,
                        stroke_fill=(*stroke_color, stroke_opacity),
                    )
                else:
                    draw.text(
                        (cursor_x, glyph_y),
                        token,
                        font=glyph_font,
                        fill=(*fill_color, fill_opacity),
                    )

                cursor_x += draw.textbbox((0, 0), token, font=glyph_font)[2]
                word_counter += 1

            cursor_y += line_height

        return overlay


def _find_active_word_index(words: List[WordSegment], current_time: float) -> int:
    for index, word in enumerate(words):
        if word.start <= current_time < word.end:
            return index
    return -1
