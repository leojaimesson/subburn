from __future__ import annotations

import os
from fractions import Fraction
from typing import List, Optional

import av

from .models.SubtitleSegment import SubtitleSegment
from .options.SubtitleStyle import SubtitleStyle
from .options.VideoBitrateOptions import VideoBitrateOptions
from .renderers.base import SubtitleRenderer
from .renderers.standard import StandardRenderer
from .utils.gpu import (
    bitrate_to_bps,
    get_default_vbv,
    get_nvenc_preset,
    is_cuda_available,
)

_DEFAULT_STYLE = SubtitleStyle()


def burn_subtitles(
    video_path: str,
    segments: List[SubtitleSegment],
    output_path: str,
    *,
    renderer: Optional[SubtitleRenderer] = None,
    style: Optional[SubtitleStyle] = None,
    bitrate: Optional[VideoBitrateOptions] = None,
    use_gpu: bool = False,
) -> str:
    active_renderer: SubtitleRenderer = renderer or StandardRenderer()
    active_style: SubtitleStyle = style or _DEFAULT_STYLE
    active_bitrate: VideoBitrateOptions = bitrate or VideoBitrateOptions()

    codec, preset = _resolve_encoder(use_gpu)

    sorted_segments = sorted(segments, key=lambda s: s.start)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with av.open(video_path) as source:
        video_in = source.streams.video[0]
        audio_in = source.streams.audio[0] if source.streams.audio else None

        fps: Fraction = video_in.average_rate or video_in.base_rate or Fraction(30, 1)

        with av.open(output_path, "w") as output:
            video_out = _add_video_output_stream(output, video_in, codec, preset)
            _apply_bitrate_options(video_out, active_bitrate, video_in.width, video_in.height, fps)

            audio_out = _add_audio_output_stream(output, audio_in)

            for packet in source.demux():
                if packet.dts is None:
                    continue

                if audio_out and packet.stream == audio_in:
                    _remux_audio_packet(packet, audio_out, output)

                elif packet.stream == video_in:
                    for frame in packet.decode():
                        rendered_frame = _render_video_frame(
                            frame, sorted_segments, active_renderer, active_style,
                            video_in.width, video_in.height,
                        )
                        rendered_frame.pts = frame.pts
                        rendered_frame.time_base = video_in.time_base
                        for encoded in video_out.encode(rendered_frame):
                            output.mux(encoded)

            for encoded in video_out.encode():
                output.mux(encoded)
            if audio_out:
                for encoded in audio_out.encode():
                    output.mux(encoded)

    return os.path.abspath(output_path)


def _resolve_encoder(use_gpu: bool) -> tuple[str, str]:
    if not use_gpu:
        return "h264", "medium"

    if not is_cuda_available():
        raise RuntimeError(
            "use_gpu=True requested but no CUDA device was found.\n"
            "Make sure:\n"
            "  1. An NVIDIA GPU is present in this machine.\n"
            "  2. The ffmpeg binary is installed with CUDA support:\n"
            "       apt install ffmpeg  |  https://ffmpeg.org/download.html\n"
            "  3. CUDA drivers are installed and up to date.\n"
            "Pass use_gpu=False to fall back to CPU encoding."
        )
    return "h264_nvenc", get_nvenc_preset()


def _add_audio_output_stream(
    output: av.container.OutputContainer,
    source_stream: Optional[av.audio.AudioStream],
) -> Optional[av.audio.AudioStream]:
    if source_stream is None:
        return None
    return output.add_stream("aac", rate=source_stream.codec_context.sample_rate)


def _add_video_output_stream(
    output: av.container.OutputContainer,
    source_stream: av.video.VideoStream,
    codec: str,
    preset: str,
) -> av.video.VideoStream:
    video_out = output.add_stream(codec, rate=source_stream.average_rate)
    video_out.width = source_stream.width
    video_out.height = source_stream.height
    video_out.pix_fmt = "yuv420p"
    video_out.options = {"preset": preset}
    video_out.time_base = source_stream.time_base
    return video_out


def _find_active_segment(
    sorted_segments: List[SubtitleSegment],
    timestamp: float,
) -> Optional[SubtitleSegment]:
    for segment in sorted_segments:
        if segment.start > timestamp:
            break
        if segment.start <= timestamp < segment.end:
            return segment
    return None


def _render_video_frame(
    frame: av.VideoFrame,
    sorted_segments: List[SubtitleSegment],
    renderer: SubtitleRenderer,
    style: SubtitleStyle,
    width: int,
    height: int,
) -> av.VideoFrame:
    timestamp = float(frame.time)
    active_segment = _find_active_segment(sorted_segments, timestamp)
    if active_segment is None:
        rendered = frame
    else:
        if frame.width != width or frame.height != height:
            frame = frame.reformat(width=width, height=height, format="rgb24")
        rendered = renderer.render(frame, active_segment, timestamp, style)
    if rendered.width != width or rendered.height != height:
        rendered = rendered.reformat(width=width, height=height, format="rgb24")
    return rendered


def _remux_audio_packet(
    packet: av.Packet,
    audio_out: av.audio.AudioStream,
    output: av.container.OutputContainer,
) -> None:
    for audio_frame in packet.decode():
        for encoded in audio_out.encode(audio_frame):
            output.mux(encoded)


def _apply_bitrate_options(
    video_out: av.video.VideoStream,
    bitrate: VideoBitrateOptions,
    width: int,
    height: int,
    fps: Fraction,
) -> None:
    if bitrate.video_bitrate:
        bps = bitrate_to_bps(bitrate.video_bitrate)
        if bps:
            video_out.bit_rate = bps
    if bitrate.maxrate:
        video_out.options["maxrate"] = bitrate.maxrate
    if bitrate.bufsize:
        video_out.options["bufsize"] = bitrate.bufsize

    auto = (
        bitrate.auto_bitrate
        and not bitrate.video_bitrate
        and not bitrate.maxrate
        and not bitrate.bufsize
        and bitrate.cq is None
    )
    if auto:
        target_bitrate, max_bitrate, buffer_size = get_default_vbv(width, height, float(fps))
        bps = bitrate_to_bps(target_bitrate)
        if bps:
            video_out.bit_rate = bps
        video_out.options["maxrate"] = max_bitrate
        video_out.options["bufsize"] = buffer_size
