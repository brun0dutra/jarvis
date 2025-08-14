import sqlite3
import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "jarvis.db"))

def conectar_db():
    return sqlite3.connect(CAMINHO_DB)

def criar_tabelas():
    with conectar_db() as conn:
        cursor = conn.cursor()
        # Tabela comandos com nova estrutura
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comandos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modulo TEXT NOT NULL,
            acao TEXT NOT NULL,
            frase TEXT NOT NULL
        )
        """)

        # Tabela logs com coluna frase
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frase TEXT,
            acao TEXT,
            parametros TEXT,
            resposta TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()

def inserir_comando(modulo: str, acao: str, frase_exemplo: str):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comandos (modulo, acao, frase) VALUES (?, ?, ?)",
            (modulo, acao, frase_exemplo)
        )
        conn.commit()

def listar_comandos() -> list[tuple[str, str, str]]:
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT modulo, acao, frase FROM comandos")
        return cursor.fetchall()

def registrar_log(frase, acao, parametros, resposta):
    if not isinstance(parametros, (str, type(None))):
        parametros = json.dumps(parametros, ensure_ascii=False)

    if not isinstance(resposta, (str, type(None))):
        resposta = json.dumps(resposta, ensure_ascii=False)

    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (frase, acao, parametros, resposta)
            VALUES (?, ?, ?, ?)
        """, (frase, acao, parametros, resposta))
        conn.commit()
        