from TTS.api import TTS

def test_tss_w_ref():
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")

    tts.tts_to_file(
        text="สวัสดีครับ",
        speaker="Abrahan Mack",
        language='en',
        file_path='output.wav'
    )

if __name__ == '__main__':
    test_tss_w_ref()