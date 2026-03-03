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

from subburn import burn_subtitles, SubtitleSegment

segments = [
    SubtitleSegment(start=0.0,  end=3.0,  text="Welcome to SubBurn!", words=[]),
    SubtitleSegment(start=3.0,  end=6.5,  text="Burning subtitles is easy.", words=[]),
    SubtitleSegment(start=6.5,  end=10.0, text="Just pass your segments and go.", words=[]),
]

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "01_basic.mp4"),
)

print("Done →", output)
