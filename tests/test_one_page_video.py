import os
import sys
import argparse
from pathlib import Path
import subprocess

from pdf2image import convert_from_path
from gtts import gTTS
from utils import generate_audio_edge_tts


def test_one_page_video(pdf_path: str, thai_text: str, tts_engine: str) -> bool:
    """Test converting first page of pdf to video with sound"""

    print("=" * 70)
    print("Test: PDF First Page -> Video with Sound")
    print("=" * 70)
    print()

    # Create intput and output directory
    input_dir = Path("../inputs")
    input_dir.mkdir(exist_ok=True)
    output_dir = Path("../outputs")
    output_dir.mkdir(exist_ok=True)


    # Verify PDF exists
    pdf_file = input_dir / pdf_path
    if not pdf_file.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <path_to_pdf>")
        print("\nExample:")
        print(f"  python {sys.argv[0]} presentation.pdf")
        return False
    
    print(f"📄 Input PDF: {pdf_file}")
    print()

    # Step 1: Extract first page as image
    print("Step 1: Extracting first page as image,,,")
    
    try:
        images = convert_from_path(
            str(pdf_file),
            dpi=300,
            fmt='png',
            first_page=1,
            last_page=1
        )

        if not images:
            print("❌ No images extracted from PDF")
            return False
        
        image_path = output_dir / "page_001.png"
        images[0].save(image_path, 'PNG')
        print(f"  ✅ Image saved: {image_path}")
        print(f"  📐 Size: {images[0].size[0]}x{images[0].size[1]} pixels")

    except Exception as e:
        print(f"  ❌ Error extracting image: {e}")
        return False
    
    print()

    # Step 2: Generate audio
    print("Step 2: Generating Thai audio narration...")
    audio_path = output_dir / "page_001.mp3"

    try:
        
        print(f"  🎙️  Generating speech...")

        if tts_engine == 'gtts':
            tts = gTTS(text=thai_text, lang='th')
            tts.save(str(audio_path))
        elif tts_engine == 'edge_tts':
            generate_audio_edge_tts(thai_text, audio_path)

        # Get audio duration
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        duration = float(result.stdout.decode().strip())

        print(f"  ✅ Audio saved: {audio_path}")
        print(f"  ⏱️  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

    except Exception as e:
        print(f"  ❌ Error generating audio: {e}")
        return False
    
    print()

    # Step 3: Creating video
    print("Step 3: Creating video with synchronized audio...")
    video_path = output_dir / "page_001_video.mp4"

    cmd = f'''ffmpeg -loop 1 -i "{image_path}" -i "{audio_path}" \
        -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
        -pix_fmt yuv420p -shortest -y "{video_path}" 2>/dev/null'''
    
    result = os.system(cmd)

    if result == 0 and video_path.exists():
        print(f"  ✅ Video created: {video_path}")

        # Get video info
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries',
             'stream=width,height,codec_name', '-of', 'json', str(video_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        import json
        info = json.loads(result.stdout.decode())
        if info.get('streams'):
            for stream in info['streams']:
                if stream.get('width'):
                    print(f"  📹 Video: {stream.get('width')}x{stream.get('height')}, codec: {stream.get('codec_name')}")
                elif stream.get('codec_name') == 'aac':
                    print(f"  🔊 Audio: codec: {stream.get('codec_name')}")
        
        # Get file size
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"  💾 File size: {size_mb:.2f} MB")

    else:
        print(f"  ❌ Error creating video")
        return False
    
    print()
    print("=" * 70)
    print("✅ TEST SUCCESSFUL!")
    print("=" * 70)
    print()
    print("Files created:")
    print(f"  📁 Output directory: {output_dir}/")
    print(f"  🖼️  Image: {image_path.name}")
    # print(f"  🔊 Audio: {audio_path.name}")
    print(f"  📹 Video: {video_path.name}")
    
    return True


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_file', help='Input PDF file')
    parser.add_argument('-tts', choices=['gtts', 'edge_tts'], default='gtts', help='TTS engine (default: gtts)')

    args = parser.parse_args()

    thai_text = """
    สวัสดีทุกท่านนะครับ
    ยินดีต้อนรับเข้าสู่การอบรมเรื่อง ออโต้เพย์ อินเซนทีฟ แดชบอร์ด

    แดชบอร์ดตัวนี้เป็นเครื่องมือสำคัญที่จะช่วยให้ทุกคนสามารถ ดูผลงานของตัวเอง ดูผลงานของทีม และดูอินเซนทีฟที่ตัวเองมีสิทธิ์ได้รับแบบชัดเจน

    แทนที่เราจะต้องรอรายงานหรือคำนวณตัวเลขเอง ตอนนี้ทุกคนสามารถตรวจสอบข้อมูลทั้งหมดได้จากหน้าจอเดียวแบบเรียลไทม์
    """

    # Run test
    success = test_one_page_video(args.pdf_file, thai_text, args.tts)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
