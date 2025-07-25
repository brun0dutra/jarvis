import sqlite3
import os

# Caminho absoluto para o arquivo atual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto para o banco de dados na pasta ../data
CAMINHO_DB = os.path.join(BASE_DIR, "..", "data", "jarvis.db")
CAMINHO_DB = os.path.abspath(CAMINHO_DB)  # normaliza

def conectar_db():
    return sqlite3.connect(CAMINHO_DB)

def criar_tabelas():
    with conectar_db() as conn:
        cursor = conn.cursor()
        # Tabela de comandos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comandos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT NOT NULL,
            frase TEXT NOT NULL
        )
        """)
        # Tabela de logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT,
            parametros TEXT,
            resposta TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def inserir_comando(acao: str, frase: str):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comandos (acao, frase) VALUES (?, ?)", (acao, frase))
        conn.commit()

def listar_comandos() -> list[tuple[str, str]]:
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT acao, frase FROM comandos")
        return cursor.fetchall()

def registrar_log(frase: str, acao: str, parametros: dict, resposta: str):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (frase, acao, parametros, resposta)
            VALUES (?, ?, ?, ?)
        """, (frase, acao, str(parametros), resposta))
        conn.commit()

