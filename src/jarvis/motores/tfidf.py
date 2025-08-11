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

    def normalizar_numeros(self, frase: str) -> str:
        # Substitui números inteiros e decimais por [NUM]
        return re.sub(r'\b\d+(\.\d+)?\b', '[NUM]', frase)

    def interpretar(self, frase: str) -> tuple[str, dict, dict]:
        frase_normalizada = self.normalizar_numeros(frase)
        entrada = self.vetor.transform([frase_normalizada])
        similaridades = cosine_similarity(entrada, self.matriz)

        indice = similaridades.argmax()
        acao_completa = self.mapeamento[indice]

        try:
            modulo = carregar_modulo(acao_completa)
            parametros, faltando = modulo.extrair_parametros(frase)
            return acao_completa, parametros, faltando
        except Exception as e:
            print(f"[Erro ao extrair parâmetros]: {e}")
            return acao_completa, {}, {}
