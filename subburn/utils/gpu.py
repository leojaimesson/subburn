import subprocess
from fractions import Fraction
from functools import lru_cache
from typing import Optional, Tuple

import av


def is_cuda_available() -> bool:
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-init_hw_device", "cuda=cuda:0",
                "-filter_hw_device", "cuda",
                "-f", "lavfi",
                "-i", "nullsrc",
                "-frames:v", "1",
                "-f", "null",
                "-"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False


@lru_cache(maxsize=1)
def get_nvenc_preset() -> str:
    candidates = ["p4", "p5", "p6", "p7", "slow", "medium", "fast", "default"]
    try:
        proc = subprocess.run(
            ["ffmpeg", "-hide_banner", "-h", "encoder=h264_nvenc"],
            capture_output=True,
            text=True,
            check=False,
        )
        text = (proc.stdout or "") + (proc.stderr or "")
        for preset in candidates:
            if preset in text:
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


