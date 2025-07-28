from interfaces.base import InterfaceBase
from core.ouvido import escutar_ate_parar
from config.setting import CONFIG

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