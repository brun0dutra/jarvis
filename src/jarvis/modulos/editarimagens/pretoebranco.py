from modulos.base import ModuloBase
import re
from PIL import Image

class Pretoebranco(ModuloBase):
    def __init__(self):
        pass

    def extrair_parametros(self, frase: str, **dados) -> str: # Deixar preto e branco
        parametros = {}
        faltando = {}

        imagens = dados.get("imagens", [])
        parametros["imagem"] = imagens[0]

        return parametros, faltando
    
    def executar(self, **kwargs):
        # Abrir a imagem
        img = Image.open(kwargs.get("imagem"))

        # Converter para preto e branco (escala de cinza)
        preto_e_branco = img.convert("L")

        caminho = "/home/brunodutra/Documentos/Programador/Jarvis/src/jarvis/modulos/editarimagens/editada/foto_pb.jpg"

        # Salvar o resultado
        preto_e_branco.save(caminho)

        return caminho, "Foto editada para preto e branco."


