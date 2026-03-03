from __future__ import annotations

from typing import List, Optional, Tuple

from PIL import ImageColor, ImageDraw, ImageFont

from ..enums.TextAlign import TextAlign
from ..options.SubtitleStyle import SubtitleStyle
from ..types.BoxShadow import BoxShadow


def load_font(style: SubtitleStyle) -> ImageFont.FreeTypeFont:
    size = int(style.font_size)
    if style.font_path:
        return ImageFont.truetype(style.font_path, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def load_font_at_size(font_path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(font_path, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def wrap_text(
    text: str,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> List[str]:
    lines: List[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def compute_block_position(
    W: int,
    H: int,
    block_w: int,
    block_h: int,
    style: SubtitleStyle,
) -> Tuple[int, int]:
    pad = style.padding
    pos_key = style.position.value if hasattr(style.position, "value") else str(style.position)
    positions = {
        "top_left":      (pad, pad),
        "top_center":    ((W - block_w) // 2, pad),
        "top_right":     (W - block_w - pad, pad),
        "center":        ((W - block_w) // 2, (H - block_h) // 2),
        "bottom_left":   (pad, H - block_h - pad),
        "bottom_center": ((W - block_w) // 2, H - block_h - pad),
        "bottom_right":  (W - block_w - pad, H - block_h - pad),
    }
    x, y = positions.get(pos_key, ((W - block_w) // 2, H - block_h - pad))
    return (
        max(pad, min(x, W - block_w - pad)),
        max(pad, min(y, H - block_h - pad)),
    )


def line_x_offset(origin_x: int, block_width: int, line_width: int, align: TextAlign) -> int:
    if align == TextAlign.LEFT:
        return origin_x
    if align == TextAlign.RIGHT:
        return origin_x + (block_width - line_width)
    return origin_x + (block_width - line_width) // 2


def split_color_and_opacity(
    value: object,
) -> Tuple[Tuple[int, int, int], int]:
    if value is None:
        return (255, 255, 255), 255
    if isinstance(value, str):
        rgb = ImageColor.getrgb(value)
        return (int(rgb[0]), int(rgb[1]), int(rgb[2])), 255
    if isinstance(value, (list, tuple)):
        if len(value) >= 4:
            r, g, b, a = value[:4]
            opacity = int(a * 255) if isinstance(a, float) and a <= 1 else int(a)
            return (int(r), int(g), int(b)), max(0, min(opacity, 255))
        if len(value) == 3:
            r, g, b = value
            return (int(r), int(g), int(b)), 255
    return (255, 255, 255), 255


def normalize_box_shadows(style: SubtitleStyle) -> List[dict]:
    raw = style.box_shadow
    if raw is None:
        return []
    if isinstance(raw, (dict, BoxShadow)):
        raw = [raw]
    raw = style.box_shadow
    if raw is None:
        return []
    if isinstance(raw, (dict, BoxShadow)):
        raw = [raw]

    shadows: List[dict] = []
    for entry in raw:
        if isinstance(entry, BoxShadow):
            color, opacity = split_color_and_opacity(entry.color)
            offset = entry.offset
            blur = entry.blur
        elif isinstance(entry, dict):
            color, opacity = split_color_and_opacity(entry.get("color", (0, 0, 0, 0.5)))
            offset = entry.get("offset", (0, 0))
            if not isinstance(offset, (list, tuple)) or len(offset) < 2:
                offset = (0, 0)
            blur = int(entry.get("blur", 0) or 0)
        else:
            continue
        shadows.append(
            {
                "color": color,
                "opacity": opacity,
                "offset": (int(offset[0]), int(offset[1])),
                "blur": max(0, blur),
            }
        )
    return shadows


def circle_offsets(radius: int) -> List[Tuple[int, int]]:
    r = int(max(0, radius or 0))
    if r <= 0:
        return [(0, 0)]
    offsets = []
    r2 = r * r
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r2:
                offsets.append((dx, dy))
    return offsets
