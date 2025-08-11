# motores/motor_cohere.py
import cohere
import numpy as np
from motores.base import MotorInterpretacao
from core.executor import carregar_modulo
from database.gerenciador import conectar_db

COHERE_API_KEY = "gMLqBwIZGdD5Aa1jYLpUKO4ZLGJpeOSZ7gsuzdBt"  # Defina via env var se preferir
MODEL = "embed-v4.0"

class MotorCohere(MotorInterpretacao):
    def __init__(self):
        self.frases = []
        self.mapeamento = []
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            # Tenta buscar com as descrições, mas funciona mesmo sem elas
            try:
                cursor.execute("SELECT modulo, acao, frase, desc_modulo, desc_acao FROM comandos")
                linhas = cursor.fetchall()
                for modulo, acao, frase, desc_modulo, desc_acao in linhas:
                    contexto = f"{frase} || {desc_modulo or ''} || {desc_acao or ''}"
                    self.frases.append(contexto.strip())
                    self.mapeamento.append(f"{modulo}.{acao}")
            except Exception:
                # Fallback: sem descrições
                cursor.execute("SELECT modulo, acao, frase FROM comandos")
                linhas = cursor.fetchall()
                for modulo, acao, frase in linhas:
                    self.frases.append(frase)
                    self.mapeamento.append(f"{modulo}.{acao}")

        self.cohere_client = cohere.Client(COHERE_API_KEY)
        self.embeddings_base = self._gerar_embeddings(self.frases)

    def _gerar_embeddings(self, textos):
        resp = self.cohere_client.embed(
            texts=textos,
            model=MODEL,
            input_type="text"
        )
        return np.array(resp.embeddings)

    def interpretar(self, frase: str) -> tuple[str, dict, dict]:
        emb_entrada = self._gerar_embeddings([frase])[0]
        similaridades = np.dot(self.embeddings_base, emb_entrada) / (
            np.linalg.norm(self.embeddings_base, axis=1) * np.linalg.norm(emb_entrada)
        )

        indice = np.argmax(similaridades)
        acao_completa = self.mapeamento[indice]

        try:
            modulo = carregar_modulo(acao_completa)
            parametros, faltando = modulo.extrair_parametros(frase)
            return acao_completa, parametros, faltando
        except Exception as e:
            print(f"[Erro ao extrair parâmetros]: {e}")
            return acao_completa, {}, {}
