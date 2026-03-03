# SubBurn

Burn subtitles directly onto video frames.

SubBurn reads a list of timed text segments, renders them onto each video frame with Pillow, and re-encodes the result using PyAV. It ships three rendering modes out of the box:

| Renderer | Style | Behaviour |
|---|---|---|
| `StandardRenderer` | `SubtitleStyle` | Static block text — same appearance for the entire segment |
| `HighlightRenderer` | `HighlightStyle` | Colours the **currently spoken** word; rest stays in base colour |
| `KaraokeRenderer` | `KaraokeStyle` | Fills **already-spoken** words with a second colour as they finish — classic karaoke fill-in |

---

## Installation

```bash
pip install subburn
```

---

## Quick start

```python
from subburn import burn_subtitles, SubtitleSegment, SubtitleStyle, Position

segments = [
    SubtitleSegment(start=0.0, end=3.0, text="Hello, world!", words=[]),
    SubtitleSegment(start=3.0, end=6.0, text="SubBurn is easy to use.", words=[]),
]

burn_subtitles(
    "input.mp4",
    segments,
    "output.mp4",
    style=SubtitleStyle(
        font_path="path/to/font.ttf",
        font_size=52,
        position=Position.BOTTOM_CENTER,
        color=(255, 255, 255),
        stroke_color=(0, 0, 0),
        stroke_width=2,
    ),
)
```

---

## Highlight mode

Highlights the word currently being spoken, leaving the rest of the line in the base colour.

```python
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
        end=4.0,
        text="Hello beautiful world",
        words=[
            WordSegment(word="Hello",     start=0.0, end=1.2),
            WordSegment(word="beautiful", start=1.2, end=2.5),
            WordSegment(word="world",     start=2.5, end=4.0),
        ],
    ),
]

burn_subtitles(
    "input.mp4",
    segments,
    "output.mp4",
    renderer=HighlightRenderer(),
    style=HighlightStyle(
        font_path="path/to/font.ttf",
        highlight_color=(255, 215, 0),
        zoom_scale=1.1,
    ),
)
```

---

## Karaoke mode

Fills already-spoken words with `spoken_color` as the video progresses — the classic karaoke sing-along fill-in effect.

```python
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
]

burn_subtitles(
    "input.mp4",
    segments,
    "output.mp4",
    renderer=KaraokeRenderer(),
    style=KaraokeStyle(
        font_path="path/to/font.ttf",
        spoken_color=(255, 215, 0),
    ),
)
```

---

## Adapters

SubBurn ships adapters that convert different subtitle sources directly into segments.

| Adapter | Source |
|---|---|
| `WhisperAdapter` | OpenAI Whisper result dict |
| `WhisperXAdapter` | WhisperX result dict |
| `SRTAdapter` | `.srt` file path or raw SRT string |
| `VTTAdapter` | `.vtt` file path or raw WebVTT string |

### OpenAI Whisper

```python
import whisper
from subburn import burn_subtitles, WhisperAdapter

model = whisper.load_model("base")
result = model.transcribe("input.mp4", word_timestamps=True)

segments = WhisperAdapter(result).get_segments()
burn_subtitles("input.mp4", segments, "output.mp4")
```

### WhisperX

```python
import whisperx
from subburn import burn_subtitles, WhisperXAdapter

# ... run whisperx transcription + alignment ...

segments = WhisperXAdapter(result, include_speaker=True).get_segments()
burn_subtitles("input.mp4", segments, "output.mp4", renderer=KaraokeRenderer())
```

### SRT files

```python
from subburn import burn_subtitles, SRTAdapter

# From a file
segments = SRTAdapter("subtitles.srt").get_segments()

# Or from a raw SRT string
raw_srt = """
1
00:00:00,000 --> 00:00:03,000
Hello, world!

2
00:00:03,000 --> 00:00:06,000
SubBurn supports SRT files natively.
"""
segments = SRTAdapter(raw_srt).get_segments()
burn_subtitles("input.mp4", segments, "output.mp4")
```

### WebVTT files

```python
from subburn import burn_subtitles, VTTAdapter

# From a file
segments = VTTAdapter("subtitles.vtt").get_segments()

# Or from a raw VTT string (e.g. downloaded from YouTube)
raw_vtt = """
WEBVTT

00:00:00.000 --> 00:00:03.000
Hello, world!

00:00:03.000 --> 00:00:06.000
SubBurn supports WebVTT files natively.
"""
segments = VTTAdapter(raw_vtt).get_segments()
burn_subtitles("input.mp4", segments, "output.mp4")
```

---

## Styling reference

```python
from subburn import SubtitleStyle, Position, BoxShadow, TextAlign, TextCase

style = SubtitleStyle(
    font_path="path/to/font.ttf",
    font_size=48,
    position=Position.BOTTOM_CENTER,
    padding=40,
    max_width_ratio=0.9,
    line_spacing=6,
    color=(255, 255, 255),
    stroke_color=(0, 0, 0),
    stroke_width=2,
    box_shadow=BoxShadow(
        color=(0, 0, 0, 0.6),
        offset=(3, 3),
        blur=4,
    ),
    text_case=TextCase.UPPER,
    text_align=TextAlign.CENTER,
)
```

### Position values

| Value | Description |
|---|---|
| `Position.TOP_LEFT` | Top-left corner |
| `Position.TOP_CENTER` | Top, horizontally centred |
| `Position.TOP_RIGHT` | Top-right corner |
| `Position.CENTER` | Screen centre |
| `Position.BOTTOM_LEFT` | Bottom-left corner |
| `Position.BOTTOM_CENTER` | Bottom, horizontally centred *(default)* |
| `Position.BOTTOM_RIGHT` | Bottom-right corner |

---

## Text & language support

SubBurn delegates all text rendering to **Pillow**, so Unicode is supported natively for any language — as long as the font file contains the required glyphs.

| Script | Support |
|---|---|
| Latin, Cyrillic, Greek, accented characters | ✅ |
| Emoji | ✅ |
| CJK, RTL, complex shaping | ❌ Not supported |

Always supply a font file whose glyph coverage matches the target language.

---

## GPU encoding

Pass `use_gpu=True` to use NVIDIA NVENC hardware encoding. Requires an NVIDIA GPU and CUDA drivers.

```python
burn_subtitles("input.mp4", segments, "output.mp4", use_gpu=True)
```

---

## Bitrate control

```python
from subburn import burn_subtitles, VideoBitrateOptions

burn_subtitles(
    "input.mp4",
    segments,
    "output.mp4",
    bitrate=VideoBitrateOptions(
        auto_bitrate=False,
        video_bitrate="4M",
        maxrate="6M",
        bufsize="8M",
    ),
)
```

---

## Requirements

- Python ≥ 3.10
- [PyAV](https://pyav.org/) ≥ 12.0
- [Pillow](https://pillow.readthedocs.io/) ≥ 10.0
- [NumPy](https://numpy.org/) ≥ 1.24

---

## License

MIT
