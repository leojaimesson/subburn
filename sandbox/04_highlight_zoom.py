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

from subburn import (
    burn_subtitles,
    HighlightRenderer,
    HighlightStyle,
    SubtitleSegment,
    WordSegment,
)

segments = [
    SubtitleSegment(
        start=0.0,
        end=5.0,
        text="Every word pops out",
        words=[
            WordSegment(word="Every", start=0.0, end=1.0),
            WordSegment(word="word",  start=1.0, end=2.1),
            WordSegment(word="pops",  start=2.1, end=3.4),
            WordSegment(word="out",   start=3.4, end=5.0),
        ],
    ),
]

style = HighlightStyle(
    font_path=FONT,
    font_size=48,
    color=(220, 220, 220),
    highlight_color=(255, 80, 80),
    stroke_color=(0, 0, 0),
    stroke_width=2,
    zoom_scale=1.3,
)

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "04_highlight_zoom.mp4"),
    renderer=HighlightRenderer(),
    style=style,
)

print("Done →", output)
