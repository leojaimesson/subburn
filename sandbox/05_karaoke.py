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
    KaraokeRenderer,
    KaraokeStyle,
    SubtitleSegment,
    WordSegment,
)

segments = [
    SubtitleSegment(
        start=0.0,
        end=4.0,
        text="Hello beautiful world",
        words=[
            WordSegment(word="Hello",     start=0.0, end=1.2),
            WordSegment(word="beautiful", start=1.2, end=2.5),
            WordSegment(word="world",     start=2.5, end=4.0),
        ],
    ),
    SubtitleSegment(
        start=4.5,
        end=8.0,
        text="Karaoke subtitles are fun",
        words=[
            WordSegment(word="Karaoke",   start=4.5, end=5.2),
            WordSegment(word="subtitles", start=5.2, end=6.1),
            WordSegment(word="are",       start=6.1, end=6.6),
            WordSegment(word="fun",       start=6.6, end=8.0),
        ],
    ),
]

style = KaraokeStyle(
    font_path=FONT,
    font_size=52,
    color=(255, 255, 255),
    spoken_color=(255, 215, 0),
    stroke_color=(0, 0, 0),
    stroke_width=2,
)

output = burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "05_karaoke.mp4"),
    renderer=KaraokeRenderer(),
    style=style,
)

print("Done →", output)
