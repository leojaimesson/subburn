from subburn import burn_subtitles, SubtitleStyle, Position, SRTAdapter

segments = SRTAdapter("subtitles.srt").get_segments()

raw_srt = """
1
00:00:00,000 --> 00:00:03,000
Hello, world!

2
00:00:03,000 --> 00:00:06,000
SubBurn supports SRT files natively.
"""
segments = SRTAdapter(raw_srt).get_segments()

burn_subtitles(
    "input.mp4",
    segments,
    "output/11_srt_adapter.mp4",
    style=SubtitleStyle(
        font_path="assets/roboto/Roboto-Bold.ttf",
        font_size=52,
        position=Position.BOTTOM_CENTER,
        color=(255, 255, 255),
        stroke_color=(0, 0, 0),
        stroke_width=2,
    ),
)
