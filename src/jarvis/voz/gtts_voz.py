from gtts import gTTS
import pygame
import time
import tempfile
from voz.base import LocutorBase

class GttsLocutor(LocutorBase):
    def falar(self, texto: str):
        try:
            tts = gTTS(text=texto, lang='pt')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tts.save(tmpfile.name)

                pygame.mixer.init()
                pygame.mixer.music.load(tmpfile.name)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
        except Exception as e:
            print(f"[Erro na fala com gTTS]: {e}")

