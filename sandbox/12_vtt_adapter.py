from subburn import burn_subtitles, SubtitleStyle, Position, VTTAdapter

segments = VTTAdapter("subtitles.vtt").get_segments()

raw_vtt = """
WEBVTT

00:00:00.000 --> 00:00:03.000
Hello, world!

00:00:03.000 --> 00:00:06.000
SubBurn supports WebVTT files natively.
"""
segments = VTTAdapter(raw_vtt).get_segments()

burn_subtitles(
    "input.mp4",
    segments,
    "output/12_vtt_adapter.mp4",
    style=SubtitleStyle(
        font_path="assets/roboto/Roboto-Bold.ttf",
        font_size=52,
        position=Position.BOTTOM_CENTER,
        color=(255, 255, 255),
        stroke_color=(0, 0, 0),
        stroke_width=2,
    ),
)
