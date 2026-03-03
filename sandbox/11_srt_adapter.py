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
from subburn.adapters import SRTAdapter

raw_srt = """\
1
00:00:00,000 --> 00:00:03,000
Hello, world!

2
00:00:03,000 --> 00:00:06,000
SubBurn supports SRT files natively.
"""

segments = SRTAdapter(raw_srt).get_segments()

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "11_srt_adapter.mp4"),
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
