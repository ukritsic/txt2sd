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

    parser.add_argument('-p', '--pdf_path', help='Input pdf file')
    parser.add_argument('-o', '--output', default='./src/outputs', help='Output directory')
    parser.add_argument('-s', '--script_path', default='./inputs/script.jsonl', help='presentation script file')

    args = parser.parse_args()

    if not Path(args.pdf_path).exists():
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)

    converter = PDFToVideoConverter(args.pdf_path, args.script_path)
    converter.convert()

if __name__ == '__main__':
    main()
