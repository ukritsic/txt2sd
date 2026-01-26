import sys
import argparse
from pathlib import Path

from utils import PDFToVideoConverter

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="PDF to Video with TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Common parameters
    parser.add_argument('-p', '--pdf_path', help='Input pdf file')
    parser.add_argument('-o', '--output', default='./src/outputs', help='Output directory')
    parser.add_argument('-s', '--script_path', default='./inputs/script.jsonl', help='presentation script file')
    parser.add_argument('--tts', choices=['edge_tts', 'gtts'], default='edge_tts', help='TTS engine')

    # Edge TTS specific
    parser.add_argument('--edge-rate', default='+0%', 
                        help='Speaking rate (-100%% to +100%%, e.g., "+20%%")')
    parser.add_argument('--edge-pitch', default='+0Hz',
                        help='Pitch adjustment (-100Hz to +100Hz. e.g., "+10Hz")')
    parser.add_argument('--edge-volume', default='+0%',
                        help='Volume adjustment (-100% to + 100%, e.g., "+50%")')

    args = parser.parse_args()

    for key, value in vars(args).items():
        print(f"{key}: {value}")

    if not Path(args.pdf_path).exists():
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)

    converter = PDFToVideoConverter(args.pdf_path, args.script_path)
    converter.convert(tts_engine=args.tts,
                    edge_rate=args.edge_rate,
                    edge_pitch=args.edge_pitch,
                    edge_volume=args.edge_volume)

if __name__ == '__main__':
    main()