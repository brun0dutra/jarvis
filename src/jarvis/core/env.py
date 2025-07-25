import os
from dotenv import load_dotenv

def env():
    # Caminho da raiz do projeto (um nível acima deste arquivo)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ENV_PATH = os.path.join(BASE_DIR, ".env")
    ENV_EXAMPLE_PATH = os.path.join(BASE_DIR, ".env.example")

    # Verifica se .env existe, senão cria a partir do .env.example
    if not os.path.exists(ENV_PATH):
        print(".env não encontrado. Criando a partir do .env.example...")
        if os.path.exists(ENV_EXAMPLE_PATH):
            with open(ENV_EXAMPLE_PATH) as example, open(ENV_PATH, "w") as env:
                env.write(example.read())
            print(".env criado. Preencha com suas informações.")
        else:
            print(".env.example não encontrado na raiz. Abortando.")
            exit(1)