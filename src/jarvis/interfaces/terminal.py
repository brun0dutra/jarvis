from interfaces.base import InterfaceBase

class InterfaceTerminal(InterfaceBase):
    def receber_entrada(self, prompt: str = "") -> str:
        return input(prompt)

    def exibir_resposta(self, texto: str):
        print(f"Jarvis: {texto}")