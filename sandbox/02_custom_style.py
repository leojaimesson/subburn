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

from subburn import burn_subtitles, SubtitleSegment, SubtitleStyle

segments = [
    SubtitleSegment(start=0.0, end=4.0, text="Custom font and color!", words=[]),
    SubtitleSegment(start=4.0, end=8.0, text="Positioned at the top-center.", words=[]),
]

style = SubtitleStyle(
    font_path=FONT,
    font_size=56,
    color=(255, 230, 50),
    stroke_color=(0, 0, 0),
    stroke_width=3,
    position="top_center",
    padding=30,
    max_width_ratio=0.85,
    line_spacing=8,
)

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "02_custom_style.mp4"),
    style=style,
)

print("Done →", output)
