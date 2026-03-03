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

from subburn import burn_subtitles, SubtitleStyle, Position
from subburn.adapters import VTTAdapter

raw_vtt = """\
WEBVTT

00:00:00.000 --> 00:00:03.000
Hello, world!

00:00:03.000 --> 00:00:06.000
SubBurn supports WebVTT files natively.
"""

segments = VTTAdapter(raw_vtt).get_segments()

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "12_vtt_adapter.mp4"),
    style=SubtitleStyle(
        font_path=FONT,
        font_size=52,
        position=Position.BOTTOM_CENTER,
        color=(255, 255, 255),
        stroke_color=(0, 0, 0),
        stroke_width=2,
    ),
)

print("Done →", output)
