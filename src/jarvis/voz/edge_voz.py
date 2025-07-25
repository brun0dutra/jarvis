import asyncio
import edge_tts
import tempfile
import pygame
import time
import os
from voz.base import LocutorBase

class EdgeLocutor(LocutorBase):
    async def gerar_audio(self, texto: str, arquivo: str):
        comunicador = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")
        await comunicador.save(arquivo)

    def falar(self, texto: str):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                asyncio.run(self.gerar_audio(texto, tmpfile.name))

                pygame.mixer.init()
                pygame.mixer.music.load(tmpfile.name)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                os.remove(tmpfile.name)
        except Exception as e:
            print(f"[Erro na fala com Edge TTS]: {e}")
