from pathlib import Path
import sys

root = str(Path(__file__).parent.parent.absolute())
if root not in sys.path:
    sys.path.insert(0, root)

ASSETS = Path(__file__).parent / "assets"
VIDEO  = str(ASSETS / "video.mp4")
FONT   = str(ASSETS / "roboto/font.ttf")
OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

from subburn import burn_subtitles, SubtitleSegment, SubtitleStyle, TextCase, TextAlign

segments = [
    SubtitleSegment(start=0.0, end=3.0, text="This will be UPPERCASE", words=[]),
    SubtitleSegment(start=3.0, end=6.0, text="Aligned to the left side", words=[]),
    SubtitleSegment(start=6.0, end=9.0, text="And this one is right-aligned text", words=[]),
]

style_upper_left = SubtitleStyle(
    font_path=FONT,
    font_size=48,
    color=(255, 255, 255),
    stroke_color=(0, 0, 0),
    stroke_width=2,
    text_case=TextCase.UPPER,
    text_align=TextAlign.LEFT,
    position="bottom_left",
)

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "05_upper_left.mp4"),
    style=style_upper_left,
)
print("UPPER+LEFT →", output)

style_lower_right = SubtitleStyle(
    font_path=FONT,
    font_size=44,
    color=(200, 255, 200),
    stroke_color=(0, 80, 0),
    stroke_width=2,
    text_case=TextCase.LOWER,
    text_align=TextAlign.RIGHT,
    position="bottom_right",
)

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "05_lower_right.mp4"),
    style=style_lower_right,
)
print("LOWER+RIGHT →", output)
