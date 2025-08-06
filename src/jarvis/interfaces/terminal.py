from interfaces.base import InterfaceBase
from core.ouvido import escutar_ate_parar
from core.locutor import carregar_locutor
from config.setting import CONFIG
import pygame, time, os

class InterfaceTerminal(InterfaceBase):
    def receber_entrada(self, prompt: str = "") -> str:

        frase = input(prompt)
        mic = CONFIG.get("microfone", "ligado")

        if mic == "ligado":
            if frase in ["1"]:
                frase = escutar_ate_parar()
                return frase
            else:
                return frase

        return frase

    def exibir_resposta(self, texto: str):
        print(f"Jarvis: {texto}")

    def falar_resposta(self, texto):
        locutor = carregar_locutor()
        caminho_do_audio = locutor(texto)

        if caminho_do_audio:

            try:
                pygame.mixer.init()
                pygame.mixer.music.load(caminho_do_audio)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            finally:
                if caminho_do_audio:
                    os.remove(caminho_do_audio)
