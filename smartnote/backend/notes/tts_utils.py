from gtts import gTTS
from io import BytesIO
import pygame

def speak_text(text: str, lang: str = "ja"):
    """
    Đọc văn bản ra âm thanh bằng gTTS + pygame,
    phát trực tiếp mà không tạo file trên ổ đĩa.

    :param text: Nội dung muốn đọc
    :param lang: Mã ngôn ngữ (vd: 'ja' cho tiếng Nhật, 'en' cho tiếng Anh)
    """
    if not text.strip():
        raise ValueError("Văn bản trống!")

    # Tạo đối tượng gTTS
    tts = gTTS(text=text, lang=lang)

    # Lưu vào bộ nhớ (BytesIO)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)

    # Phát trực tiếp bằng pygame
    mp3_fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pass  # chờ phát xong

# if __name__ == "__main__":
#     content = input("Nhập nội dung để đọc thành tiếng: ")
#     speak_text(content, lang="ja")