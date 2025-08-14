from modulos.base import ModuloBase
import re, os, logging
from icrawler.builtin import GoogleImageCrawler

class Google(ModuloBase):
    def __init__(self):
        pass

    def extrair_parametros(self, frase, **dados): #Baixar 2 imagem de uma Casa Laranja
        parametros = {}
        faltando = {}

        ## Extrair número de imagens
        numeros = dados.get("numeros", [])
        num_imagens = int(numeros[0])
        
        # Extrair termo da imagem (após "uma ")
        match_termo = re.search(r"uma (.+)", frase)

        if match_termo:
            termo = match_termo.group(1)
            parametros["imagem"] = termo
        else:
            faltando["imagem"] = "Qual conteudo da imagem ?"
        
        parametros["numero"] = num_imagens

        return parametros, faltando
    
    def executar(self, **kwargs):
        # Desativa logs de info e warning
        logging.getLogger("icrawler").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        logging.getLogger().setLevel(logging.CRITICAL)
        
        termo = kwargs.get("imagem", "jarvis")
        num_imagens = kwargs.get("numero", 1)

        pasta = f"src/jarvis/modulos/baixarimagens/imagens/temp/{termo}"
        os.makedirs(pasta, exist_ok=True)

        # Cria o crawler para Google
        crawler = GoogleImageCrawler(storage={'root_dir': pasta})
        crawler.crawl(keyword=termo, max_num=num_imagens)

        # Lista todos os arquivos baixados com caminho completo
        arquivos = os.listdir(pasta)

        todos = []
        for arquivo in arquivos:
            todos.append(f"{pasta}/{arquivo}")

        return todos, f"Aqui estao suas imagens de {termo}"

