

import argparse
import os
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    ImageClip,
)


def create_text_image_clip(
    text: str,
    font_size: int,
    color: str,
    duration: float,
    video_width: int,
    video_height: int,
    font_path: Optional[str] = None,
    vertical_offset_ratio: float = 0.12,
) -> Optional[ImageClip]:
    """
    Create an ImageClip containing the given text, positioned horizontally centered
    and slightly below the vertical center by vertical_offset_ratio of the height.

    Uses Pillow to render text to an RGBA image to avoid ImageMagick dependency.
    """
    if not text:
        return None

    # Choose font
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Try a common font; fallback to default if unavailable
            font = ImageFont.truetype("Arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Measure text
    tmp_image = Image.new("RGBA", (video_width, video_height), (0, 0, 0, 0))
    drawer = ImageDraw.Draw(tmp_image)
    # textbbox returns (left, top, right, bottom)
    bbox = drawer.textbbox((0, 0), text, font=font, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Render text to a tightly fitting transparent canvas with small padding
    padding_x, padding_y = 20, 10
    text_image = Image.new(
        "RGBA", (text_width + padding_x, text_height + padding_y), (0, 0, 0, 0)
    )
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((padding_x // 2, padding_y // 2), text, font=font, fill=color)

    # Convert to numpy array and build ImageClip
    text_array = np.array(text_image)
    text_clip = ImageClip(text_array, is_mask=False).with_duration(duration)

    # Compute position: horizontally centered, slightly below vertical center
    x = (video_width - text_clip.w) // 2
    y_center = video_height // 2
    y = int(y_center + vertical_offset_ratio * video_height - text_clip.h // 2)
    return text_clip.with_position((x, y))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Concatenate two videos and overlay text slightly below the center using MoviePy."
        )
    )
    parser.add_argument("--input1", "-i1", required=True, help="Path to first input video")
    parser.add_argument("--input2", "-i2", required=True, help="Path to second input video")
    parser.add_argument(
        "--output", "-o", default="output.mp4", help="Path to output video file"
    )
    parser.add_argument(
        "--text",
        "-t",
        default="",
        help="Text to overlay slightly below the center (optional)",
    )
    parser.add_argument(
        "--font_path",
        default=None,
        help="Path to a .ttf/.otf font file to render the text (optional)",
    )
    parser.add_argument(
        "--font_size", type=int, default=64, help="Font size for overlaid text"
    )
    parser.add_argument(
        "--text_color",
        default="white",
        help="Text color (name like 'white' or hex like '#ffffff')",
    )
    parser.add_argument(
        "--offset_ratio",
        type=float,
        default=0.12,
        help=(
            "How far below the vertical center to place the text, as a fraction of video height"
        ),
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Override output FPS (defaults to combined clip's FPS)",
    )
    parser.add_argument(
        "--preset",
        default="medium",
        help="x264 encoding preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=20,
        help="x264 Constant Rate Factor (lower is higher quality; 18-23 is typical)",
    )

    args = parser.parse_args()

    clip1: Optional[VideoFileClip] = None
    clip2: Optional[VideoFileClip] = None
    combined = None
    final = None

    try:
        clip1 = VideoFileClip(args.input1)
        clip2 = VideoFileClip(args.input2)

        # Compose to handle different sizes/audio
        combined = concatenate_videoclips([clip1, clip2], method="compose")

        target_fps = args.fps or getattr(combined, "fps", None) or 24

        text_clip = create_text_image_clip(
            text=args.text,
            font_size=args.font_size,
            color=args.text_color,
            duration=combined.duration,
            video_width=combined.w,
            video_height=combined.h,
            font_path=args.font_path,
            vertical_offset_ratio=args.offset_ratio,
        )

        if text_clip is not None:
            final = CompositeVideoClip([combined, text_clip])
        else:
            final = combined

        # Write output video
        final.write_videofile(
            args.output,
            codec="libx264",
            audio_codec="aac",
            fps=target_fps,
            preset=args.preset,
            threads=os.cpu_count() or 4,
            ffmpeg_params=["-crf", str(args.crf)],
        )

    finally:
        # Close all clips to release file handles
        for c in (final, combined, clip1, clip2):
            try:
                if c is not None:
                    c.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()


