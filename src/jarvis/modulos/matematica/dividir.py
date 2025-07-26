import re
from modulos.base import ModuloBase

class Dividir(ModuloBase):
    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        numeros = list(map(int, re.findall(r"\d+", frase)))
        parametros = {}
        faltando = {}

        if len(numeros) >= 2:
            parametros["a"] = numeros[0]
            parametros["b"] = numeros[1]
        elif len(numeros) == 1:
            parametros["a"] = numeros[0]
            faltando["b"] = "Qual o segundo número?"
        else:
            faltando["a"] = "Qual o primeiro número?"
            faltando["b"] = "Qual o segundo número?"

        return parametros, faltando

    def executar(self, **kwargs) -> str:
        a = int(kwargs.get("a", 0))
        b = int(kwargs.get("b", 0))
        resultado = a / b
        return f"O resultado de {a} dividido por {b} é {resultado}"