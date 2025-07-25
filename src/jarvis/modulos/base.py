from abc import ABC, abstractmethod

class ModuloBase(ABC):
    @abstractmethod
    def executar(self, **kwargs) -> str:
        """
        Executa o comando principal do módulo.
        Deve retornar uma string com a resposta.
        """
        pass
