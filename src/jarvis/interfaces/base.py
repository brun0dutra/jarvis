from abc import ABC, abstractmethod

class InterfaceBase(ABC):
    @abstractmethod
    def receber_entrada(self) -> str:
        pass

    @abstractmethod
    def exibir_resposta(self, conteudo):
        pass
