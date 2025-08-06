import asyncio
import edge_tts
import tempfile
from voz.base import LocutorBase

class EdgeLocutor(LocutorBase):
    async def gerar_audio(self, texto: str, arquivo: str):
        comunicador = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")
        await comunicador.save(arquivo)

    def gerar_fala(self, texto: str) -> str:
        """
        Gera o áudio da fala e retorna o caminho do arquivo gerado (.mp3).
        Não toca o áudio.
        """
        try:
            tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            caminho = tmpfile.name
            tmpfile.close()  # Fechar para o edge-tts poder escrever nele

            asyncio.run(self.gerar_audio(texto, caminho))

            return caminho  # Caminho do arquivo gerado
        except Exception as e:
            print(f"[Erro na fala com Edge TTS]: {e}")
            return None
        