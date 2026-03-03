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

from subburn import burn_subtitles, SubtitleSegment, SubtitleStyle, VideoBitrateOptions
from subburn.utils.gpu import is_cuda_available

segments = [
    SubtitleSegment(start=0.0, end=5.0, text="High-quality encode", words=[]),
]

style = SubtitleStyle(
    font_path=FONT,
    font_size=48,
    color=(255, 255, 255),
    stroke_color=(0, 0, 0),
    stroke_width=2,
)

burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "07_auto_bitrate_cpu.mp4"),
    style=style,
)
print("Auto bitrate (CPU) done")

bitrate_fixed = VideoBitrateOptions(
    auto_bitrate=False,
    video_bitrate="6M",
    maxrate="8M",
    bufsize="16M",
)

burn_subtitles(
    VIDEO,
    segments,
    str(OUTPUT / "07_fixed_bitrate_cpu.mp4"),
    style=style,
    bitrate=bitrate_fixed,
)
print("Fixed 6M bitrate (CPU) done")

if is_cuda_available():
    burn_subtitles(
        VIDEO,
        segments,
        str(OUTPUT / "07_gpu_nvenc.mp4"),
        style=style,
        use_gpu=True,
        bitrate=VideoBitrateOptions(
            auto_bitrate=False,
            cq=18,
        ),
    )
    print("GPU (NVENC CQ-18) done")
else:
    print("GPU not available – skipping NVENC example.")
    print("Install: apt install ffmpeg  and ensure an NVIDIA GPU + drivers are present.")

