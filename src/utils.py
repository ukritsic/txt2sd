import os
import asyncio
import subprocess
from pathlib import Path
from typing import List
import json

try:
    from pdf2image import convert_from_path
    # from moviepy.editor import ImageClip, AudioClip, concatenate_videoclips
except ImportError:
    print("Installing required packages...")
    os.system("uv add pdf2image pdfplumber Pillow")
    from pdf2image import convert_from_path


class PDFToVideoConverter:
    """Convert PDF pages to video with audio narration"""

    def __init__(self, pdf_path: str, script_path: str , output_dir: str = "./outputs"):
        self.pdf_path = Path(pdf_path)
        self.script_path = Path(script_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.images_dir = self.output_dir / "images"
        self.audio_dir = self.output_dir / "audio"
        self.video_dir = self.output_dir / "videos"
        self.images_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        self.video_dir.mkdir(exist_ok=True)

        self.page_data = []

    @staticmethod
    def _get_audio_duration(output_path):
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',  '-of', 'default=noprint_wrappers=1:nokey=1', str(output_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        duration = float(result.stdout.decode().strip())

        return duration
    
    def extract_text_from_jsonl(self) -> List[str]:
        """Extract text content from jsonl file"""
        print("Extracting txt from .jsonl file...")

        texts = []
        with open(self.script_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                
                page = data["page"]
                text = data["text"]
                print(f"Page {page}: {text}")

                texts.append(text)
        return texts

    def extract_pages_as_images(self, dpi: int = 300) -> List[Path]:
        """Extract PDF pages as high-quality images"""
        print(f"[>] Converting PDF to images (DPI: {dpi})...")

        images = convert_from_path(
            self.pdf_path,
            dpi=dpi,
            fmt='png',
            thread_count=4
        )
        
        image_paths = []
        for i, image in enumerate(images, 1):
            image_path = self.images_dir / f"page_{i:03d}.png"
            image.save(image_path, 'PNG', quality=95)
            image_paths.append(image_path)
            print(f"    Save page {i}/{len(images)}.png")

        return image_paths
    
    def generate_audio_edge_tts(self, text: str, output_path: Path, voice: str = 'th-TH-PremwadeeNeural'):
        """Generate audio using Edge TTS (Microsoft's high-quality TTS)
        
        Popular Thai voices:
        - th-TH-PremwadeeNeural (Female)
        - th-TH-NiwatNeural (Male)
        """

        try:
            import edge_tts
        except ImportError:
            print("Installing edge-tts...")
            os.system("uv add edge-tts")
            import edge_tts

        if not text.strip():
            # Create silent audio for empty pages
            duration = 2.0
            os.system(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t {duration} -q:a 9 -acodec libmp3lame {output_path} -y 2>/dev/null")
            return duration
        
        # Generate speech using edge-tts
        async def generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

        # Run async function
        asyncio.run(generate())

        duration = self._get_audio_duration(output_path)

        return duration
    
    def generate_audio_gtts(self, text: str, output_path: Path):
        pass

    def create_page_videos(self, image_paths: List[Path], texts: List[str],
                        tts_engine: str = 'edge_tts', lang: str = 'th',
                        voice: str = 'th-TH-PremwadeeNeural') -> List[Path]:
        """Create individual video clips for each page with audio"""
        
        print(f"\nGenerating audio and videos using {tts_engine}...")
        if tts_engine == 'edge_tts':
            print(f"    Voice: {voice}")

        video_paths = []

        for i, (img_path, text) in enumerate(zip(image_paths, texts), 1):
            audio_path = self.audio_dir / f"page_{i:03d}.mp3"
            video_path = self.video_dir / f"page_{i:03d}_video.mp4"

            # Generate audio
            print(f"\n  Page {i}/{len(image_paths)}:")
            print("     Generating audio...")

            if tts_engine == 'edge_tts':
                duration = self.generate_audio_edge_tts(text, audio_path, voice)
            else:
                pass

            print(f"    Audio duration: {duration: .2f}s")

            # Create video from image + audio
            print(f"    Creating video clip...")
            cmd = f"""ffmpeg -loop 1 -i "{img_path}" -i "{audio_path}" \
                -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
                -pix_fmt yuv420p -shortest -y "{video_path}" 2>/dev/null"""

            os.system(cmd)
            video_paths.append(video_path)

            # Store page data
            self.page_data.append({
                'page': i,
                'image': str(img_path),
                'audio': str(audio_path),
                'video': str(video_path),
                'duration': duration,
                'text_preview': text[:100] + '...' if len(text) > 100 else text                
            }) 

        return video_paths

    def merge_video(self, video_paths: List[Path], output_name: str = "final_video.mp4") :
        """Merge all page videos into one video"""
        print("\nMerging videos...")

        # Create concat file
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.absolute()}'\n")

        # Merge videos
        final_output = self.output_dir / output_name
        cmd = f'ffmpeg -f concat -safe 0 -i "{concat_file}" -c copy "{final_output}" -y 2>/dev/null'
        os.system(cmd)

        print(f"\n✓ Final video created: {final_output}")

        # Save metadata
        metadata_file = self.output_dir / "metadata.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'pdf_file': str(self.pdf_path),
                    'total_pages': len(video_paths),
                    'total_duration': sum(p['duration'] for p in self.page_data),
                    'output_video': str(final_output),
                    'pages': self.page_data                
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save metadta: {e}")    

        print(f"✓ Metadata saved: {metadata_file}")
        
        return final_output
    
    def convert(self, dpi: int = 300, tts_engine: str = 'edge_tts',
                lang: str = 'th', voice: str = 'th-TH-PremwadeeNeural',
                output_name: str = 'final_video.mp4'):
        """Full conversion pipeline"""
        print(f"=" * 60)
        print(f"PDF to Video Converter")
        print(f"=" * 60)
        print(f"Input: {self.pdf_path}")
        print(f"Output: {self.output_dir}")
        print(f"TTS Engine: {tts_engine}")
        if tts_engine == 'edge_tts':
            print(f"Voice: {voice}")
        else:
            print(f"Language: {lang}")
        print(f"=" * 60)

        # Step 1: Extract pages as images
        image_paths = self.extract_pages_as_images(dpi=dpi)

        # Step 2: Extract text
        texts = self.extract_text_from_jsonl()

        # Step 3: Create videos with audio
        video_paths = self.create_page_videos(image_paths, texts, tts_engine, lang, voice)

        # Step 4: Merge all videos
        final_video = self.merge_video(video_paths, output_name)

        print(f"\n" + "=" * 60)
        print(f"  Total pages: {len(image_paths)}")
        print(f"  Total duration: {sum(p['duration'] for p in self.page_data):.2f}s")
        print(f"  Final video: {final_video}")
        print(f"=" * 60)
        
        return final_video    

    
if __name__ == '__main__':

    pdf_path = '../inputs/autopay.pdf'
    script_path = '../inputs/script.jsonl'

    converter = PDFToVideoConverter(pdf_path, script_path)

    converter.convert()
