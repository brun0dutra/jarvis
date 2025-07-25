from abc import ABC, abstractmethod

class LoginBase(ABC):
    @abstractmethod
    def autenticar(self) -> bool:
        pass
