from fractions import Fraction
from functools import lru_cache
from typing import Optional, Tuple

import av


@lru_cache(maxsize=1)
def is_cuda_available() -> bool:
    try:
        if "h264_nvenc" not in av.codecs_available:
            return False
        codec = av.codec.Codec("h264_nvenc", "w")
        if hasattr(codec, "hardware_configs"):
            return any(cfg.is_supported for cfg in codec.hardware_configs)
        return codec.is_encoder
    except Exception:
        return False


@lru_cache(maxsize=1)
def get_nvenc_preset() -> str:
    candidates = ["p4", "p5", "p6", "p7", "slow", "medium", "fast"]
    try:
        codec = av.codec.Codec("h264_nvenc", "w")
        option_names = {opt.name for opt in codec.options}
        for preset in candidates:
            if preset in option_names:
                return preset
    except Exception:
        pass
    return "default"


def get_video_info(
    path: str,
) -> Tuple[Optional[int], Optional[int], Optional[float], bool]:
    with av.open(path) as container:
        v_stream = next(iter(container.streams.video), None)
        a_stream = next(iter(container.streams.audio), None)

        width: Optional[int] = v_stream.width if v_stream else None
        height: Optional[int] = v_stream.height if v_stream else None
        fps: Optional[float] = None
        if v_stream:
            rate: Fraction = v_stream.average_rate or v_stream.base_rate
            if rate:
                fps = float(rate)

        has_audio = a_stream is not None

    return width, height, fps, has_audio


def _get_default_bitrate(
    width: int,
    height: int,
    fps: float | None = None,
    base_bitrate_mbps: float = 6.0,
) -> str:
    fps = fps or 30.0
    mpix = (width * height) / 1_000_000.0
    base_mpix = (1080 * 1920) / 1_000_000.0
    scale = (mpix / base_mpix) * (fps / 30.0)
    bitrate_mbps = max(2.0, min(base_bitrate_mbps * scale, 16.0))
    return f"{bitrate_mbps:.1f}M"


def get_default_vbv(
    width: int,
    height: int,
    fps: float | None = None,
) -> tuple[str, str, str]:
    bitrate = _get_default_bitrate(width, height, fps)
    value = float(bitrate.replace("M", ""))
    maxrate = f"{value * 1.2:.1f}M"
    bufsize = f"{value * 2.0:.1f}M"
    return bitrate, maxrate, bufsize


def bitrate_to_bps(value: str | None) -> int | None:
    if not value:
        return None
    v = value.strip().upper()
    try:
        if v.endswith("K"):
            return int(float(v[:-1]) * 1_000)
        if v.endswith("M"):
            return int(float(v[:-1]) * 1_000_000)
        return int(float(v))
    except ValueError:
        return None


