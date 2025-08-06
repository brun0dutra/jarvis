from abc import ABC, abstractmethod

class LocutorBase(ABC):
    @abstractmethod
    def gerar_fala(self, texto: str):
        pass