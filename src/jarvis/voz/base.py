from abc import ABC, abstractmethod

class LocutorBase(ABC):
    @abstractmethod
    def falar(self, texto: str):
        pass