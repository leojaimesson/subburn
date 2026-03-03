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

from subburn import burn_subtitles, SubtitleStyle, KaraokeRenderer
from subburn.adapters import WhisperXAdapter

whisperx_result = {
    "segments": [
        {
            "start": 0.0,
            "end": 3.5,
            "text": "Hello world",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 1.2, "score": 0.98},
                {"word": "world", "start": 1.2, "end": 3.5, "score": 0.95},
            ],
        },
        {
            "start": 4.0,
            "end": 7.0,
            "text": "Subtitles are easy",
            "words": [
                {"word": "Subtitles", "start": 4.0, "end": 5.0, "score": 0.97},
                {"word": "are",       "start": 5.0, "end": 5.6, "score": 0.99},
                {"word": "easy",      "start": 5.6, "end": 7.0, "score": 0.96},
            ],
        },
    ],
}

whisperx_result_diarized = {
    "segments": [
        {**whisperx_result["segments"][0], "speaker": "SPEAKER_00"},
        {**whisperx_result["segments"][1], "speaker": "SPEAKER_01"},
    ],
}

segments = WhisperXAdapter(whisperx_result).get_segments()

style = SubtitleStyle(
    font_path=FONT,
    font_size=50,
    color=(255, 255, 255),
    stroke_color=(0, 0, 0),
    stroke_width=2,
)

burn_subtitles(
    VIDEO, segments, str(OUTPUT / "09_whisperx_karaoke.mp4"),
    renderer=KaraokeRenderer(), style=style,
)
print("Karaoke done")

segments_speakers = WhisperXAdapter(whisperx_result_diarized, include_speaker=True).get_segments()

burn_subtitles(VIDEO, segments_speakers, str(OUTPUT / "09_whisperx_speakers.mp4"), style=style)
print("With speakers done")
