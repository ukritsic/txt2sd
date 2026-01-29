import os
import edge_tts
import subprocess
from gtts import gTTS
from pathlib import Path
from pdf2image import convert_from_path
import asyncio

def test_build1page():
    pdf_path = "./inputs/AutopayTH.pdf"
    thai_text = "สวัสดีค่ะทุกคน วันนี้เราจะมาแนะนำเครื่องมือสำคัญที่ช่วยให้พี่ๆ เอบีดีสามารถติดตามผลงานออโต้เพย์ของแต่ละพื้นที่ได้ง่ายขึ้น นั่นก็คือ “ออโต้เพย์ อินเซ็นทีฝ แดชบอร์ด” ค่ะ แดชบอร์ดนี้ถูกออกแบบมาเพื่อให้เราดูผลงานปัจจุบันในพื้นที่ความรับผิดชอบของตัวเอง รวมถึงผลงานของทีมและยังบอกด้วยว่าเรามีสิทธิ์ได้รับอินเซ็นทีฝเท่าไหร่ หรือจะต้องทำเพิ่มอีกเท่าไหร่เพื่อให้ได้อินเซ็นทีฝที่สูงขึ้น วันนี้เราจะมาดูฟีเจอร์ต่างๆ ไปด้วยกันแบบสบายๆ ไม่ต้องกังวลนะคะแม้ไม่เคยใช้แดชบอร์ดมาก่อนก็เข้าใจได้แน่นอนค่ะ"

    out_dir = Path('./tests/outputs')
    out_dir.mkdir(exist_ok=True)

    image_file = out_dir / 'page_001.png'
    audio_file = out_dir / 'page_001.mp3'
    video_file = out_dir / 'test_video.mp4'
    
    # Extract image from pdf file
    images = convert_from_path(
        pdf_path,
        dpi=300,
        fmt='png',
        first_page=1,
        last_page=1
    )
    images[0].save(image_file)

    if not thai_text.strip():
        duration = 2.0
        os.system(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t {duration} -q:a 9 -acodec libmp3lame {image_file} -y 2>/dev/null")

    voice = 'th-TH-PremwadeeNeural'
    rate = '-7%'
    pitch = '+30Hz'
    volume = '+0%'
     
    async def generate():
        communicate = edge_tts.Communicate(
                                        thai_text, 
                                        voice,
                                        rate=rate,
                                        pitch=pitch,
                                        volume=volume
                                    )
        await communicate.save(str(audio_file))

    # asyncio.run(generate())

    tts = gTTS(text=thai_text, lang='th')
    tts.save(str(audio_file))

    result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',  '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
    )
    duration = float(result.stdout.decode().strip())


    cmd = f"""ffmpeg -loop 1 -i "{image_file}" -i "{audio_file}" \
                -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
                -pix_fmt yuv420p -shortest -y "{video_file}" 2>/dev/null"""
    
    os.system(cmd)

if __name__ == '__main__':
    test_build1page()

