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

        intencoes = {
            "temperatura": ["temperatura", "calor", "frio", "sensação", "termica", "maxima", "minima"],
            "chuva": ["psossibilidade", "precipitação", "probabilidade de chuva", "chuva"],
            "volume": ["milimetros", "volume"],
            "nuvens":["nuvem", "nuvens"],
            "umidade": ["umidade"],
            "vento": ["vento", "rajada", "direção"],
            "visibilidade": ["visibilidade", "nevoa", "serração"],
            "uv": ["uv", "raios uv", "ultravioleta", "raios ultravioleta"],
            "pressao": ["pressao", "atmosferica"],
            "orvalho": ["orvalho", "ponto de orvalho"],
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
        nome_valor_um = ""
        nome_valor_dois = ""
        cor_valor_um = ""
        cor_valor_dois = ""

        for item in dados_usar:
            labels.append(formatador(item["dt"]))

            if dado == "temperatura":
                if modo == "horas":
                    valores.append(item["temp"])
                    valoresdois.append(item["feels_like"])
                    numero_de_valores = 2
                    nome_valor_um = "Temperatura"
                    nome_valor_dois = "Senssação Termica"
                    cor_valor_um = "orange"
                    cor_valor_dois = "green"
                else:
                    valores.append(item["temp"]["max"]) 
                    valoresdois.append(item["temp"]["min"])
                    numero_de_valores = 2
                    nome_valor_um = "Maxima"
                    nome_valor_dois = "Minima"
                    cor_valor_um = "red"
                    cor_valor_dois = "blue"

            elif dado == "chuva":
                valores.append(item.get("pop", 0) * 100)
                numero_de_valores = 1
                nome_valor_um = "Probabilidade de chuva"
                cor_valor_um = "blue"

            elif dado == "volume":
                valores.append(item.get("rain", 0))
                numero_de_valores = 1
                nome_valor_um = "Milimetros de chuva"
                cor_valor_um = "blue"

            elif dado == "nuvens":
                valores.append(item["clouds"])
                numero_de_valores = 1
                nome_valor_um = "Nuvens"
                cor_valor_um = "blue"

            elif dado == "umidade":
                valores.append(item["humidity"])
                numero_de_valores = 1
                nome_valor_um = "Umidade"
                cor_valor_um = "blue"

            elif dado == "vento":
                valores.append(item["wind_speed"] * 3.6)
                valoresdois.append(item.get("wind_gust") * 3.6)
                numero_de_valores = 2
                nome_valor_um = "Vento"
                nome_valor_dois = "Rajadas"
                cor_valor_um = "blue"
                cor_valor_dois = "red"

            elif dado == "visibilidade":
                valores.append(item.get("visibility"))
                numero_de_valores = 1
                nome_valor_um = "Visibilidade"
                cor_valor_um = "blue"

            elif dado == "uv":
                valores.append(item.get("uvi", 0))
                numero_de_valores = 1
                nome_valor_um = "Raios uv"
                cor_valor_um = "red"

            elif dado == "pressao":
                valores.append(item.get("pressure", 0))
                numero_de_valores = 1
                nome_valor_um = "Pressão Atmosferica"
                cor_valor_um = "red"

            elif dado == "orvalho":
                valores.append(item.get("dew_point", 0))
                numero_de_valores = 1
                nome_valor_um = "Ponto do orvalho"
                cor_valor_um = "blue"

            

        # === VISUAL ===
        plt.style.use('default')  # estilo padrão do matplotlib
        plt.figure(figsize=(12, 5))

        # Plot
        if numero_de_valores == 1:
            plt.plot(labels, valores, marker='o', linestyle='-', color=cor_valor_um, linewidth=2, label=dado)
        elif numero_de_valores == 2:
            plt.plot(labels, valores, marker='o', linestyle='-', color=cor_valor_um, linewidth=2, label=nome_valor_um)
            plt.plot(labels, valoresdois, marker='o', linestyle='-', color=cor_valor_dois, linewidth=2, label=nome_valor_dois)

        # Título e rótulos (sem cor branca, deixa padrão para o estilo default)
        plt.title(f"{dado}", fontsize=16, fontweight='bold')
        plt.xlabel("Tempo", fontsize=12)
        plt.ylabel("°C" if dado == "temperatura" else "%", fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.4)

        # Legenda
        plt.legend()

        # Valores nos pontos
        for x, y in zip(labels, valores):
            plt.text(x, y, f"{y:.1f}", ha='center', va='bottom', fontsize=8)
        if numero_de_valores == 2:
            for x, y in zip(labels, valoresdois):
                plt.text(x, y, f"{y:.1f}", ha='center', va='bottom', fontsize=8)

        # Bordas mais suaves
        ax = plt.gca()
        for spine in ax.spines.values():
            spine.set_color('gray')

        plt.tight_layout()

        # Salvar imagem
        nome_arquivo = f"src/jarvis/modulos/clima/graficos/grafico_{dado}_{modo}_{quantidade}.png"
        plt.savefig(nome_arquivo, dpi=100)
        plt.close()

        texto = nome_arquivo
        fala = f"Aqui está o gráfico de {dado} para {quantidade} {modo}."
        return texto, fala
