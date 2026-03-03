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
    SubtitleSegment(start=0.0, end=4.0, text="Soft drop shadow", words=[]),
    SubtitleSegment(start=4.0, end=8.0, text="Hard offset shadow", words=[]),
    SubtitleSegment(start=8.0, end=12.0, text="Layered neon glow", words=[]),
]

style_soft = SubtitleStyle(
    font_path=FONT,
    font_size=52,
    color=(255, 255, 255),
    box_shadow={
        "color": (0, 0, 0, 0.6),
        "offset": (4, 4),
        "blur": 6,
    },
)

burn_subtitles(VIDEO, segments[:1], str(OUTPUT / "06_soft_shadow.mp4"), style=style_soft)
print("Soft shadow done")

style_hard = SubtitleStyle(
    font_path=FONT,
    font_size=52,
    color=(255, 255, 255),
    box_shadow={
        "color": (30, 30, 30, 200),
        "offset": (6, 6),
        "blur": 0,
    },
)

burn_subtitles(VIDEO, segments[1:2], str(OUTPUT / "06_hard_shadow.mp4"), style=style_hard)
print("Hard shadow done")

style_glow = SubtitleStyle(
    font_path=FONT,
    font_size=52,
    color=(255, 255, 255),
    box_shadow=[
        {"color": (0, 180, 255, 0.8), "offset": (0, 0), "blur": 8},
        {"color": (0,  80, 200, 0.5), "offset": (0, 0), "blur": 14},
        {"color": (0,   0,   0, 0.4), "offset": (3, 3), "blur": 2},
    ],
)

burn_subtitles(VIDEO, segments[2:3], str(OUTPUT / "06_glow.mp4"), style=style_glow)
print("Glow done")
