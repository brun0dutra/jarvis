from motores.base import MotorInterpretacao
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.executor import carregar_modulo
from database.gerenciador import conectar_db
import re

class MotorTFIDF(MotorInterpretacao):
    def __init__(self):
        self.frases = []
        self.mapeamento = []

        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT modulo, acao, frase FROM comandos")
            linhas = cursor.fetchall()

            for modulo, acao, frase in linhas:
                self.frases.append(frase)
                self.mapeamento.append(f"{modulo}.{acao}")  # Ex: clima.previsaohora

        self.vetor = TfidfVectorizer()
        self.matriz = self.vetor.fit_transform(self.frases)

    def normalizar_e_extrair(self, frase: str) -> tuple[str, dict]:
        dados = {}

        # Imagens
        extensoes_imagem = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
        # Regex que captura caminhos completos, com espaços e acentos
        padrao_img = r'(/[\w\s\-\./\\áàâãéèêíïóôõöúçÇÁÉÍÓÚ]+?\.(?:' + '|'.join([ext.lstrip('.') for ext in extensoes_imagem]) + r'))'

        imagens = re.findall(padrao_img, frase)
        dados["imagens"] = imagens
        frase = re.sub(padrao_img, '[IMG]', frase)

        # Documentos
        extensoes_doc = ('.txt', '.doc', '.docx')
        padrao_doc = r'[\w\-/\\:.]+\.(?:' + '|'.join([ext.lstrip('.') for ext in extensoes_doc]) + r')\b'
        docs = re.findall(padrao_doc, frase)
        dados["docs"] = docs
        frase = re.sub(padrao_doc, '[DOC]', frase)

        # Áudios
        extensoes_audio = ('.mp3', '.wav', '.ogg')
        padrao_audio = r'[\w\-/\\:.]+\.(?:' + '|'.join([ext.lstrip('.') for ext in extensoes_audio]) + r')\b'
        audios = re.findall(padrao_audio, frase)
        dados["audios"] = audios
        frase = re.sub(padrao_audio, '[AUD]', frase)

        # Números_Inteiros
        numeros = list(map(float, re.findall(r"\d+(?:\.\d+)?", frase)))
        dados["numeros"] = numeros
        frase = re.sub(r'\b\d+(\.\d+)?\b', '[NUM]', frase)

        return frase, dados

    def interpretar(self, frase: str) -> tuple[str, dict, dict]:
        frase_normalizada, dados = self.normalizar_e_extrair(frase)

        entrada = self.vetor.transform([frase_normalizada])
        similaridades = cosine_similarity(entrada, self.matriz)

        indice = similaridades.argmax()
        acao_completa = self.mapeamento[indice]

        try:
            modulo = carregar_modulo(acao_completa)
            parametros, faltando = modulo.extrair_parametros(frase, **dados)
            return acao_completa, parametros, faltando
        except Exception as e:
            print(f"[Erro ao extrair parâmetros]: {e}")
            return acao_completa, {}, {}
