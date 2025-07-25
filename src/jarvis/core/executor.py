import importlib

def carregar_modulo(acao: str):
    try:
        partes = acao.split(".")
        if len(partes) == 1:
            modulo_nome = partes[0]
            classe_nome = partes[0].capitalize()
        else:
            *pacote, classe = partes
            modulo_nome = ".".join(pacote + [classe])
            classe_nome = classe.capitalize()

        caminho = f"modulos.{modulo_nome}"
        modulo = importlib.import_module(caminho)
        classe = getattr(modulo, classe_nome)
        return classe()
    except Exception as e:
        print(f"[Erro ao carregar módulo {acao}]: {e}")
        raise


def executar(acao: str, **kwargs):
    try:
        # Ação vem no formato: "matematica.somar"
        modulo = importlib.import_module(f"modulos.{acao}")
        classe_nome = acao.split(".")[-1].capitalize()
        classe = getattr(modulo, classe_nome)
        instancia = classe()
        return instancia.executar(**kwargs)

    except Exception as e:
        print(f"[Erro ao executar {acao}]: {e}")
        return "Desculpe, ocorreu um erro ao executar o comando."
