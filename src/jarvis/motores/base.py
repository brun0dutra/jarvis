from abc import ABC, abstractmethod

class MotorInterpretacao(ABC):
    @abstractmethod
    def interpretar(self, frase: str) -> tuple[str, dict]:
        pass
