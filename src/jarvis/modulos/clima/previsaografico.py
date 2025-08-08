from modulos.base import ModuloBase
from dotenv import load_dotenv
import requests
import os
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class Previsaografico(ModuloBase):
    def __init__(self):
        load_dotenv()
        self._token = os.getenv("API_CLIMA")
        self._lat = -31.31487713699913
        self._lon = -54.1174584168256
        self._link = f"https://api.openweathermap.org/data/3.0/onecall?lat={self._lat}&lon={self._lon}&appid={self._token}&units=metric&lang=pt_br"

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        frase = frase.lower()
        parametros = {}
        faltando = {}

        match = re.search(r"(\d{1,2})\s*(h|hora|horas|d|dia|dias)?", frase)
        if match:
            qtd = int(match.group(1))
            if "d" in match.group(2) if match.group(2) else "":
                parametros["modo"] = "dias"
                parametros["quantidade"] = max(1, min(qtd, 7))
            else:
                parametros["modo"] = "horas"
                parametros["quantidade"] = max(1, min(qtd, 48))
        else:
            faltando["modo"] = "Para horas ou dias ?"
            faltando["quantidade"] = "Qual o periodo ?"

        if "chuva" in frase:
            parametros["dado"] = "chuva"
        elif "volume" in frase:
            parametros["dado"] = "volume"
        elif "temperatura" in frase:
            parametros["dado"] = "temperatura"
        elif "nuvens" in frase:
            parametros["dado"] = "nuvens"
        elif "umidade" in frase:
            parametros["dado"] = "umidade"
        elif "vento" in frase:
            parametros["dado"] = "vento"
        elif "visibilidade" in frase:
            parametros["dado"] = "visibilidade"
        elif "uv" in frase:
            parametros["dado"] = "uv"
        elif "orvalho" in frase:
            parametros["dado"] = "orvalho"
        else:
            faltando["dado"] = "Qual informação do clima ?"

        return parametros, faltando

    def executar(self, **kwargs):
        modo = kwargs.get("modo", "horas")
        quantidade = int(kwargs.get("quantidade", 48))
        dado = kwargs.get("dado", "temperatura")

        url = self._link
        dados = requests.get(url).json()
        timezone = dados.get("timezone_offset", 0)

        if modo == "horas":
            dados_usar = dados["hourly"][:quantidade]
            formatador = lambda ts: (datetime.utcfromtimestamp(ts) + timedelta(seconds=timezone)).strftime('%d/%m %Hh')
        else:
            dados_usar = dados["daily"][:quantidade]
            formatador = lambda ts: datetime.utcfromtimestamp(ts).strftime('%a %d/%m')

        labels = []
        valores = []
        valoresdois = []
        numero_de_valores = 0

        for item in dados_usar:
            labels.append(formatador(item["dt"]))

            if dado == "temperatura":
                if modo == "horas":
                    valores.append(item["temp"])
                    valoresdois.append(item["feels_like"])
                    numero_de_valores = 2
                else:
                    valores.append(item["temp"]["max"]) 
                    valoresdois.append(item["temp"]["min"])
                    numero_de_valores = 2

            elif dado == "chuva":
                valores.append(item.get("pop", 0) * 100)
                numero_de_valores = 1

            elif dado == "volume":
                valores.append(item.get("rain", 0))
                numero_de_valores = 1

            elif dado == "nuvens":
                valores.append(item["clouds"])
                numero_de_valores = 1

            elif dado == "umidade":
                valores.append(item["humidity"])
                numero_de_valores = 1

            elif dado == "vento":
                valores.append(item["wind_speed"] * 3.6)
                valoresdois.append(item.get("wind_gust") * 3.6)
                numero_de_valores = 2

            elif dado == "visibilidade":
                valores.append(item.get("visibility"))
                numero_de_valores = 1

            elif dado == "uv":
                valores.append(item.get("uvi", 0))
                numero_de_valores = 1

            elif dado == "pressao":
                valores.append(item.get("pressure", 0))
                numero_de_valores = 1

            elif dado == "orvalho":
                valores.append(item.get("dew_point", 0))
                numero_de_valores = 1

            

        # === VISUAL ===
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 5))

        # Cores automáticas por tipo de dado
        cor = 'orange' if dado == 'temperatura' else 'cyan'

        # Plot
        if numero_de_valores == 1:
            plt.plot(labels, valores, marker='o', linestyle='-', color=cor, linewidth=2)
        if numero_de_valores == 2:
            plt.plot(labels, valores, marker='o', linestyle='-', color=cor, linewidth=2)
            plt.plot(labels, valoresdois, marker='o', linestyle='-', color="orange", linewidth=2)
        

        titulo = f"{dado}"
        plt.title(titulo, fontsize=16, fontweight='bold', color='white')
        plt.xlabel("Tempo", fontsize=12, color='white')
        plt.ylabel("°C" if dado == "temperatura" else "%", fontsize=12, color='white')
        plt.xticks(rotation=45, fontsize=10, color='white')
        plt.yticks(fontsize=10, color='white')
        plt.grid(True, linestyle='--', alpha=0.4)

        # Bordas mais suaves
        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_color('gray')

        plt.tight_layout()

        # Nome do arquivo com base no dado
        nome_arquivo = f"src/jarvis/modulos/clima/graficos/grafico_{dado}_{modo}_{quantidade}.png"
        plt.savefig(nome_arquivo, dpi=100)
        plt.close()

        texto = f"Gráfico de {dado} salvo em: {nome_arquivo}"
        fala = f"Aqui está o gráfico de {dado} para {quantidade} {modo}."
        return texto, fala
