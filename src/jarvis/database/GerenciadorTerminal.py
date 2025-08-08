import sqlite3
import os
from tabulate import tabulate
import pyfiglet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "jarvis.db"))
def limpar_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')


while True:

    limpar_terminal()
    titulo = pyfiglet.print_figlet(text="Comandos Do Jarvis", colors="Red", font="small")

    print("""
    [1] - Registrar nova função/frase
    [2] - Listar todos modulos
    [3] - Listar todas funções
    [4] - Listar funções por modulos
    [5] - Listar funções especificas      
    [6] - Deletar função unica
    [7] - Deletar todas funções especifica
    [8] - Deletar modulo
    [9] - Inserir varias frases para a mesma função
    [10] - Verificar similaridade de frase
    [11] - Sair
    """)

    escolha = input("Escolha uma opção: ")
    limpar_terminal()

    def conectar_db():
        return sqlite3.connect(CAMINHO_DB)

    def inserir_funcao(modulo: str, acao: str, frase: str):
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO comandos (modulo, acao, frase) VALUES (?, ?, ?)",
                (modulo, acao, frase)
            )
            conn.commit()

    def listar_modulos() -> list[str]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT modulo FROM comandos")
            return [row[0] for row in cursor.fetchall()]

    def listar_comandos() -> list[tuple[str, str, str]]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, modulo, acao, frase FROM comandos")
            return cursor.fetchall()
        
    def listar_comandos_por_modulo(modulo: str) -> list[tuple[str, str, str]]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, modulo, acao, frase FROM comandos WHERE modulo = ?",
                (modulo,)
            )
            return cursor.fetchall()
        
    def listar_comandos_por_acao(acao: str) -> list[tuple[str, str, str]]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, modulo, acao, frase FROM comandos WHERE acao = ?",
                (acao,)
            )
            return cursor.fetchall()
        
    def deletar_funcao_unica(id):
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM comandos WHERE id = ?", (id,))
            conn.commit()

    def deletar_funcoes_por_acao(acao):
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM comandos WHERE acao = ?", (acao,))
            conn.commit()
        
    def deletar_modulo(modulo):
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM comandos WHERE modulo = ?", (modulo,))
            conn.commit()

    def verificar_frase_similar(frase):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        frases = []
        mapeamento = []

        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT modulo, acao, frase FROM comandos")
            linhas = cursor.fetchall()

            for modulo, acao, frase_db in linhas:
                frases.append(frase_db)
                mapeamento.append(f"{modulo}.{acao}")  # Ex: clima.previsaohora

        vetor = TfidfVectorizer()
        matriz = vetor.fit_transform(frases)

        entrada = vetor.transform([frase])
        similaridades = cosine_similarity(entrada, matriz)[0]

        indice = similaridades.argmax()
        acao_completa = mapeamento[indice]
        frase_encontrada = frases[indice]
        similaridade_valor = similaridades[indice]

        print(f"Frase digitada: {frase}")
        print(f"Frase mais parecida no banco: {frase_encontrada}")
        print(f"Similaridade: {similaridade_valor:.4f}")
        print(f"Ação completa: {acao_completa}")
        input("Aperte ENTER para continuar !")
    

    if escolha == "1":
        modulo = input("Modulo: ")
        funcao = input("Função: ")
        frase = input("Frase: ")
        inserir_funcao(modulo=modulo, acao=funcao, frase=frase)
        print(f"Modulo {modulo}, função {funcao}, frase {frase} | Registrada com sucesso !")
        limpar_terminal()

    elif escolha == "2":
        modulos = listar_modulos()
        # Tabulate precisa de lista de listas ou tuplas
        modulos_formatado = [[modulo] for modulo in modulos]
        print(tabulate(modulos_formatado, headers=["Módulo"], tablefmt="github"))
        input("\nAperte ENTER para continuar !")
        limpar_terminal()

    elif escolha == "3":
        comandos = listar_comandos()
        headers = ["Id", "Módulo", "Ação", "Frase"]
        print(tabulate(comandos, headers=headers, tablefmt="github"))
        input("\nAperte ENTER para continuar !")
        limpar_terminal()

    elif escolha == "4":
        modulo = input("Digite o nome do módulo: ").strip().lower()
        comandos = listar_comandos_por_modulo(modulo)

        if comandos:
            headers = ["Id", "Módulo", "Ação", "Frase"]
            print(tabulate(comandos, headers=headers, tablefmt="github"))
            input("\nAperte ENTER para continuar !")
            limpar_terminal()
        else:
            print(f"Nenhum comando encontrado para o módulo '{modulo}'.")
            input("\nAperte ENTER para continuar !")
            limpar_terminal()

    elif escolha == "5":
        acao = input("Digite o nome da ação: ").strip().lower()
        comandos = listar_comandos_por_acao(acao)

        if comandos:
            headers = ["id", "Módulo", "Ação", "Frase"]
            print(tabulate(comandos, headers=headers, tablefmt="github"))
            input("\nAperte ENTER para continuar !")
            limpar_terminal()
        else:
            print(f"Nenhum comando encontrado com a ação '{acao}'.")
            input("\nAperte ENTER para continuar !")
            limpar_terminal()

    elif escolha == "6":
        id = int(input("Id da função que deseja deletar: "))
        
        if id:
            deletar_funcao_unica(id)

    elif escolha == "7":
        funcoes = input("Qual nome das funções que você deseja apagar: ")
        deletar_funcoes_por_acao(funcoes)
        print(f"Todas funções: {funcoes} foram apagadas com SUCESSO !")
        input("Aperte ENTER para continuar !")

    elif escolha == "8":
        modulo = input("Qual modulo deseja apagar: ")
        deletar_modulo(modulo)
        print(f"Modulo {modulo} deletado com SUCESSO !")
        input("Aperte ENTER para continuar !")

    elif escolha == "9":
        modulo = input("Qual modulo: ")
        funcao = input("Qual função: ")
        print("Para sair DIGITE 'sair' e APERTE ENTER !")

        while True:
            frase = input("Frase: ")
            if frase == "sair":
                break
            else:
                inserir_funcao(modulo=modulo, acao=funcao, frase=frase)
                print(f"Modulo {modulo}, função {funcao}, frase {frase} | Registrada com sucesso !")

    elif escolha == "10":
        frase = input("Frase a ser verificada: ")
        verificar_frase_similar(frase)

    elif escolha == "11":
        break