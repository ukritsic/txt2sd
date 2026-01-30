# txt2sd

A Python tool for converting PDF presentations into narrated video files using Text-to-Speech (TTS) technology. Perfect for creating automated presentation videos with Thai language support.

## Features

- **PDF to Video Conversion**: Convert PDF slides into engaging video presentations
- **Multiple TTS Engines**: 
  - Edge TTS (Microsoft Azure) - Recommended for Thai language
  - Google TTS (gTTS)
- **High-Quality Output**: Configurable DPI for image extraction (default: 300)
- **Customizable Voice Parameters**: Control rate, pitch, and volume for Edge TTS
- **Script-Based Narration**: Use JSONL format for page-by-page narration scripts
- **Automatic Merging**: Combines all pages into a single video file
- **Metadata Generation**: Saves detailed metadata about the conversion process

## Quick Start

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Extract the project
unzip txt2sd.zip
cd txt2sd

# Install dependencies
uv sync

# Run conversion
uv run src/main.py -p your-presentation.pdf -s your-script.jsonl
```

## Requirements

- Python >= 3.11
- FFmpeg (for audio/video processing)
- Poppler (for PDF to image conversion)

## Installation

### 1. Install uv

If you don't have uv installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit https://docs.astral.sh/uv/getting-started/installation/

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg poppler-utils
```

**macOS:**
```bash
brew install ffmpeg poppler
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Download Poppler from https://github.com/oschwartz10612/poppler-windows/releases

### 3. Install Project Dependencies

```bash
# Sync all dependencies from uv.lock
uv sync

# Or install in development mode
uv pip install -e .
```

## Usage

### Basic Usage

```bash
uv run src/main.py -p path/to/presentation.pdf -s path/to/script.jsonl
```

### Advanced Usage with Edge TTS Customization

```bash
uv run src/main.py \
  -p presentation.pdf \
  -s script.jsonl \
  -o ./output \
  --tts edge_tts \
  --edge-rate "+10%" \
  --edge-pitch "+15Hz" \
  --edge-volume "+0%"
```

### Command Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--pdf_path` | `-p` | Required | Input PDF file path |
| `--script_path` | `-s` | `./inputs/script.jsonl` | Narration script file (JSONL format) |
| `--output` | `-o` | `./src/outputs` | Output directory |
| `--tts` | | `edge_tts` | TTS engine (`edge_tts` or `gtts`) |
| `--edge-rate` | | `+0%` | Speaking rate (-100% to +100%) |
| `--edge-pitch` | | `+0Hz` | Pitch adjustment (-100Hz to +100Hz) |
| `--edge-volume` | | `+0%` | Volume adjustment (-100% to +100%) |

## Script Format

Create a JSONL file with narration text for each page:

```jsonl
{"page": 1, "text": "สวัสดีครับ ยินดีต้อนรับสู่งานนำเสนอ"}
{"page": 2, "text": "วันนี้เราจะมาพูดถึงหัวข้อที่น่าสนใจ"}
{"page": 3, "text": "ขอบคุณที่รับฟังครับ"}
```

Each line should contain:
- `page`: Page number (starting from 1)
- `text`: Narration text for that page

## Output Structure

After conversion, the output directory will contain:

```
outputs/
├── images/           # Extracted PNG images from PDF pages
│   ├── page_001.png
│   ├── page_002.png
│   └── ...
├── audio/            # Generated audio files
│   ├── page_001.mp3
│   ├── page_002.mp3
│   └── ...
├── videos/           # Individual page videos
│   ├── page_001_video.mp4
│   ├── page_002_video.mp4
│   └── ...
├── final_video.mp4   # Merged final video
├── metadata.json     # Conversion metadata
└── concat_list.txt   # FFmpeg concat file
```

## Example

```bash
# Convert a PDF with Thai narration using Edge TTS
uv run src/main.py \
  -p ./inputs/presentation.pdf \
  -s ./inputs/script.jsonl \
  -o ./outputs \
  --tts edge_tts \
  --edge-rate "-5%" \
  --edge-pitch "+20Hz"
```

## TTS Engines

### Edge TTS (Recommended for Thai)
- Voice: `th-TH-PremwadeeNeural` (default Thai voice)
- Customizable rate, pitch, and volume
- High-quality natural-sounding speech
- Requires internet connection

### Google TTS (gTTS)
- Simpler alternative
- Good for basic Thai narration
- Fewer customization options

## Development

### Running Tests

```bash
uv run pytest
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Sync dependencies after updating
uv sync
```

### Project Structure

```
txt2sd/
├── src/
│   ├── main.py          # CLI entry point
│   └── utils.py         # Core conversion logic
├── tests/
│   ├── test_one_page.py
│   └── test_coqui_w_ref.py
├── pyproject.toml
├── pytest.ini
└── README.md
```

## Troubleshooting

### FFmpeg not found
Ensure FFmpeg is installed and accessible in your PATH:
```bash
ffmpeg -version
```

### Poppler not found
Verify Poppler is installed:
```bash
pdftoppm -v  # Linux/Mac
```

### TTS Generation Issues
- **Edge TTS**: Check internet connection
- **gTTS**: Verify language code is correct (`th` for Thai)

## Dependencies

Main dependencies:
- `coqui-tts[codec]>=0.27.5`
- `edge-tts>=7.2.7`
- `gtts>=2.5.4`
- `pdf2image>=1.17.0`
- `pdfplumber>=0.11.9`
- `pillow>=12.1.0`
- `torch>=2.10.0`
- `torchaudio>=2.10.0`

Development dependencies:
- `pytest>=9.0.2`
