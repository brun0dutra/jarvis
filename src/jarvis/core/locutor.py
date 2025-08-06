import importlib
from config.setting import CONFIG

def carregar_locutor():
    nome = CONFIG.get("voz_metodo", "gtts")
    try:
        modulo = importlib.import_module(f"voz.{nome}_voz")
        classe = getattr(modulo, f"{nome.capitalize()}Locutor")
        instancia = classe()
        return instancia.gerar_fala
    except Exception as e:
        print(f"[Erro ao carregar locutor]: {e}")
        return lambda texto: None
