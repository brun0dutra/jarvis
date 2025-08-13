from modulos.base import ModuloBase
import sqlite3
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from zoneinfo import ZoneInfo
import calendar

class Diashistoricos(ModuloBase):
    def __init__(self):
        self._db_path = "src/jarvis/data/clima.db"

        # Mapeamento de dados para colunas no banco
        # Se o dado tem duas colunas, é (max, min)
        # Se tem só uma, é só uma coluna
        self.colunas = {
            "temperatura": ("temperatura_min", "temperatura_max", "temperatura_media"),
            "sensacao": ("sensacao_min", "sensacao_max", "sensacao_media"),
            "pressao": ("pressao_min", "pressao_max", "pressao_media"),
            "umidade": ("umidade_min", "umidade_max", "umidade_media"),
            "orvalho": ("orvalho_min", "orvalho_max", "orvalho_media"),
            "uvi": ("uvi_min", "uvi_max", "uvi_media"),
            "nuvens": ("nuvens_min", "nuvens_max", "nuvens_media"),
            "visibilidade": ("visibilidade_min", "visibilidade_max", "visibilidade_media"),
            "vento": ("vento_min", "vento_max", "vento_media"),
            "rajada": ("rajada_min", "rajada_max", "rajada_media"),
            "chuva": ("precipitacao_total",),
            "neve": ("neve_total",),
            # Pode ir adicionando o que quiser aqui...
        }

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        frase = frase.lower()
        print(frase)
        parametros = {}
        faltando = {}

        fuso_local = ZoneInfo("America/Sao_Paulo")
        hoje = datetime.now(tz=fuso_local).date()

        # -------------------------
        # Palavras-chave fixas
        # -------------------------
        if "dessa semana" in frase:
            data_inicio = hoje - timedelta(days=hoje.weekday())  # Segunda-feira
            data_fim = hoje
            parametros["modo"] = "dias"
            parametros["data_inicio"] = data_inicio
            parametros["data_fim"] = data_fim

        elif "desse mes" in frase or "desse mês" in frase:
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
            parametros["modo"] = "dias"
            parametros["data_inicio"] = data_inicio
            parametros["data_fim"] = data_fim

        elif "mes passado" in frase or "mês passado" in frase:
            primeiro_deste_mes = hoje.replace(day=1)
            ultimo_mes = primeiro_deste_mes - timedelta(days=1)
            data_inicio = ultimo_mes.replace(day=1)
            ultimo_dia_mes_passado = calendar.monthrange(ultimo_mes.year, ultimo_mes.month)[1]
            data_fim = ultimo_mes.replace(day=ultimo_dia_mes_passado)
            parametros["modo"] = "dias"
            parametros["data_inicio"] = data_inicio
            parametros["data_fim"] = data_fim

        else:
            # -------------------------
            # Fallback: últimos N dias
            # -------------------------
            match = re.search(r"(\d{1,2})\s*(d|dia|dias)?", frase)
            if match:
                qtd = int(match.group(1))
                parametros["modo"] = "dias"
                parametros["quantidade"] = max(1, min(qtd, 30))
            else:
                faltando["quantidade"] = "Qual o período (em dias)?"

        # -------------------------
        # Intenções mapeadas para dados conhecidos
        # -------------------------
        intencoes = {
            "temperatura": ["temperatura", "calor", "frio"],
            "sensacao": ["sensação térmica", "sensacao termica", "sensação", "sensacao"],
            "pressao": ["pressao", "pressão", "pressão atmosferica"],
            "umidade": ["umidade"],
            "orvalho": ["orvalho", "ponto do orvalho"],
            "uvi": ["uvi", "uv", "radiação", "radiaçao"],
            "nuvens": ["nuvens", "nuvem"],
            "visibilidade": ["visibilidade", "serração", "nevoeiro", "serraçao"],
            "vento": ["vento", "ventos", "ventania"],
            "rajada": ["rajada de vento", "rajada", "vento forte"],
            "chuva": ["chuva", "precipitação", "precipitacao", "milimetros", "volume"],
            "neve": ["neve"]
        }

        for chave, palavras in intencoes.items():
            for p in palavras:
                if re.search(rf"\b{re.escape(p)}\b", frase):
                    parametros["dado"] = chave
                    break
            if "dado" in parametros:
                break

        return parametros, faltando

    def executar(self, **kwargs):
        modo = kwargs.get("modo", "dias")
        quantidade = int(kwargs.get("quantidade", 7))
        dado = kwargs.get("dado", "temperatura")

        col = self.colunas.get(dado)
        if not col:
            return f"Desculpe, não tenho dados para '{dado}'."

        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()

        if kwargs.get("data_inicio") and kwargs.get("data_fim"):
            data_fim = kwargs.get("data_fim")
            data_inicio = kwargs.get("data_inicio")
        else:
            data_fim = datetime.utcnow().date()
            data_inicio = data_fim - timedelta(days=quantidade - 1)

        if len(col) == 3:
            col_min, col_max, col_media = col
            cursor.execute(f"""
                SELECT data, {col_min}, {col_max}, {col_media} FROM clima_dia
                WHERE data BETWEEN ? AND ?
                ORDER BY data ASC
            """, (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d')))
            resultados = cursor.fetchall()

            resultados = [
                (data, vmin if vmin is not None else 0,
                    vmax if vmax is not None else 0,
                    vmed if vmed is not None else 0)
                for data, vmin, vmax, vmed in resultados
            ]

        else:
            coluna = col[0]
            cursor.execute(f"""
                SELECT data, {coluna} FROM clima_dia
                WHERE data BETWEEN ? AND ?
                ORDER BY data ASC
            """, (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d')))
            resultados = cursor.fetchall()

            resultados = [
                (data, vmin if vmin is not None else 0,
                    vmax if vmax is not None else 0,
                    vmed if vmed is not None else 0)
                for data, vmin, vmax, vmed in resultados
            ]

        conexao.close()

        if not resultados:
            return f"Não encontrei dados para os últimos {quantidade} {modo}."

        datas = [r[0] for r in resultados]

        plt.figure(figsize=(12, 5))

        if len(col) == 3:
            minimos = [r[1] for r in resultados]
            maximos = [r[2] for r in resultados]
            medias = [r[3] for r in resultados]

            plt.plot(datas, maximos, marker='o', color='red', linewidth=2, label=f"{dado.replace('_',' ').capitalize()} Máximo")
            plt.plot(datas, minimos, marker='o', color='blue', linewidth=2, label=f"{dado.replace('_',' ').capitalize()} Mínimo")
            plt.plot(datas, medias, marker='o', color='green', linewidth=2, label=f"{dado.replace('_',' ').capitalize()} Media")

            for x, y in zip(datas, maximos):
                plt.text(x, y, f"{y:.1f}", ha='center', va='bottom', fontsize=8)
            for x, y in zip(datas, minimos):
                plt.text(x, y, f"{y:.1f}", ha='center', va='top', fontsize=8)
            for x, y in zip(datas, medias):
                plt.text(x, y, f"{y:.1f}", ha='center', va='top', fontsize=8)

            ylabel = "°C" if "temperatura" in dado or "termica" in dado else "Unidades"

        else:
            valores = [r[1] for r in resultados]

            plt.plot(datas, valores, marker='o', color='orange', linewidth=2, label=dado.capitalize())

            for x, y in zip(datas, valores):
                plt.text(x, y, f"{y:.1f}", ha='center', va='bottom', fontsize=8)

            ylabel = {
                "chuva": "mm",
                "umidade": "%",
            }.get(dado, "Unidades")

        plt.title(f"{dado.replace('_', ' ').capitalize()} dos últimos {quantidade} {modo}", fontsize=16, fontweight='bold')
        plt.xlabel("Data")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend()
        plt.tight_layout()

        caminho_img = f"src/jarvis/modulos/clima/graficos/grafico_historico_{dado}_{quantidade}{modo}.png"
        plt.savefig(caminho_img, dpi=100)
        plt.close()

        texto = caminho_img
        fala = f"Aqui está o gráfico de {dado.replace('_', ' ')} para os últimos {quantidade} {modo}."
        return texto, fala
