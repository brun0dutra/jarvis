from interfaces.base import InterfaceBase
from core.ouvido import escutar_ate_parar
from core.locutor import carregar_locutor
from config.setting import CONFIG
import pygame, time, os
from PIL import Image

class InterfaceTerminal(InterfaceBase):
    def __init__(self):
        # Extensões válidas
        self.extensoes_imagem = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    def receber_entrada(self, prompt: str = "") -> str:

        frase = input(prompt)
        mic = CONFIG.get("microfone", "ligado")

        if mic == "ligado":
            if frase in ["'"]:
                frase = escutar_ate_parar()
                return frase

        return frase

    def exibir_resposta(self, conteudo):

        # Garante que sempre vamos trabalhar com uma lista
        if not isinstance(conteudo, (list)):
            conteudo = [conteudo]

        for item in conteudo:

            # Se for imagem
            if os.path.isfile(item) and item.lower().endswith(self.extensoes_imagem):
                img = Image.open(item)
                img.show()

            # Se for texto
            print(f"Jarvis: {item}")

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
