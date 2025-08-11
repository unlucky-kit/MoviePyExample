## MoviePyExample

Concatenate two videos into one and overlay text slightly below the center using MoviePy and Pillow (no ImageMagick required).

### Requirements

- Python 3.8+
- `ffmpeg` is recommended but not strictly required (MoviePy uses `imageio-ffmpeg`). On macOS you can install via Homebrew: `brew install ffmpeg`.

### Setup

```bash
cd /Users/iurii/Desktop/Projects/ClipCut
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

Basic concatenation with overlaid text slightly below center:

```bash
python main.py \
  --input1 path/to/first.mp4 \
  --input2 path/to/second.mp4 \
  --text "Your overlay text" \
  --output output.mp4
```

#### Options

- `--input1`, `-i1` (required): Path to the first video
- `--input2`, `-i2` (required): Path to the second video
- `--output`, `-o`: Output file path (default: `output.mp4`)
- `--text`, `-t`: Text to overlay (optional)
- `--font_path`: Path to a `.ttf`/`.otf` font file (optional). If omitted, the script attempts a common system font and falls back to Pillow's default.
- `--font_size`: Text size (default: `64`)
- `--text_color`: Color name (e.g., `white`, `red`) or hex (e.g., `#ffffff`) (default: `white`)
- `--offset_ratio`: How far below the vertical center to place the text, as a fraction of video height (default: `0.12` → 12% below center)
- `--fps`: Override output FPS (defaults to the concatenated clip's FPS)
- `--preset`: x264 preset (default: `medium`)
- `--crf`: x264 CRF quality (default: `20`, lower is higher quality)

#### Examples

Overlay text 15% below center, larger font, and custom color:

```bash
python clipcut.py -i1 a.mp4 -i2 b.mp4 -t "My Title" --font_size 72 --text_color "#ffee88" --offset_ratio 0.15 -o merged.mp4
```

Use a specific font file (macOS example paths):

```bash
python clipcut.py -i1 a.mp4 -i2 b.mp4 -t "Hello" --font_path "/Library/Fonts/Arial.ttf" -o merged.mp4
```

### Notes

- The two videos are concatenated sequentially (one after the other). If you prefer crossfades or transitions, we can extend the script.
- The text overlay spans the full duration of the combined clip and is positioned slightly below the center `(center_y + offset_ratio * height)`.
- If you see font-related issues, provide a `--font_path` to a valid `.ttf`/`.otf` font on your system.


