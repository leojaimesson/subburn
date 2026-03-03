"""SubBurn – subtitle burning library."""
from importlib.metadata import version, PackageNotFoundError

from .core import burn_subtitles
from .models.SubtitleSegment import SubtitleSegment
from .models.WordSegment import WordSegment
from .options.SubtitleStyle import SubtitleStyle
from .options.KaraokeStyle import KaraokeStyle
from .options.HighlightStyle import HighlightStyle
from .options.VideoBitrateOptions import VideoBitrateOptions
from .renderers.base import SubtitleRenderer
from .renderers.standard import StandardRenderer
from .renderers.karaoke import KaraokeRenderer
from .renderers.highlight import HighlightRenderer
from .enums.TextAlign import TextAlign
from .enums.TextCase import TextCase
from .enums.Position import Position
from .types import BoxShadow, Color
from .adapters.whisper import WhisperAdapter
from .adapters.whisperx import WhisperXAdapter

try:
    __version__ = version("subburn")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "burn_subtitles",
    "SubtitleSegment",
    "WordSegment",
    "SubtitleStyle",
    "KaraokeStyle",
    "HighlightStyle",
    "VideoBitrateOptions",
    "SubtitleRenderer",
    "StandardRenderer",
    "KaraokeRenderer",
    "HighlightRenderer",
    "TextAlign",
    "TextCase",
    "Position",
    "BoxShadow",
    "Color",
    "WhisperAdapter",
    "WhisperXAdapter",
]

