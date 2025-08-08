from modulos.base import ModuloBase
from dotenv import load_dotenv
import requests
import os
import re
from datetime import datetime, timedelta

class Previsaodia(ModuloBase):
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

        # Extrair quantidade de dias (1 a 7)
        match = re.search(r"(\d{1})\s*(dias|dia)?", frase)
        if "amanha" in frase:
            parametros["quantidade_dias"] = 1
        elif match:
            qtd = int(match.group(1))
            parametros["quantidade_dias"] = max(1, min(qtd, 7))
        else:
            parametros["quantidade_dias"] = 7

        intencoes = {
            "temperatura": ["temperatura", "calor", "frio", "sensação", "termica", "uv", "sol"],
            "chuva": ["chuva", "precipitação", "probabilidade", "volume", "milímetros", "vai chover", "chove"],
            "umidade": ["umidade", "úmido", "seco"],
            "vento": ["vento", "rajada", "direção"],
            "clima": ["clima", "condição", "tempo", "nuvem", "ensolarado"],
            "visibilidade": ["visibilidade", "nevoa", "serração"],
            "pressao": ["pressao", "atmosferica"],
            "orvalho": ["orvalho", "ponto de orvalho"],
            "lua": ["lua", "fase da lua"],
        }

        for chave, palavras in intencoes.items():
            for p in palavras:
                if re.search(rf"\b{re.escape(p)}\b", frase):
                    parametros["dado"] = chave
                    break
            if "dado" in parametros:
                break

        return parametros, faltando

    def direcao_vento_em_texto(self, graus):
        direcoes = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]
        index = int((graus + 22.5) // 45) % 8
        return direcoes[index]

    def executar(self, **kwargs):
        dados = requests.get(self._link).json()
        dias = dados["daily"]
        timezone_offset = dados["timezone_offset"]
        quantidade = kwargs.get("quantidade_dias", 7)
        dado = kwargs.get("dado")
        resultado = []

        for dia in dias[:quantidade]:
            data = (datetime.utcfromtimestamp(dia["dt"]) + timedelta(seconds=timezone_offset)).strftime("%d/%m (%A)").capitalize()

            # Dados
            descricao = dia["weather"][0]["description"].capitalize()
            temperatura = dia["temp"]
            sensacao = dia["feels_like"]
            umidade = dia["humidity"]
            pressao = dia["pressure"]
            uv = dia["uvi"]
            vento = dia["wind_speed"] * 3.6
            vento_dir = dia["wind_deg"]
            rajadas = dia.get("wind_gust", 0) * 3.6
            nuvens = dia["clouds"]
            prob_chuva = dia.get("pop", 0) * 100
            volume_chuva = dia.get("rain", 0)
            volume_neve = dia.get("snow", 0)
            orvalho = dia.get("dew_point", 0)
            nascer_sol = datetime.utcfromtimestamp(dia["sunrise"] + timezone_offset).strftime("%H:%M")
            por_sol = datetime.utcfromtimestamp(dia["sunset"] + timezone_offset).strftime("%H:%M")
            nascer_lua = datetime.utcfromtimestamp(dia["moonrise"] + timezone_offset).strftime("%H:%M")
            por_lua = datetime.utcfromtimestamp(dia["moonset"] + timezone_offset).strftime("%H:%M")
            fase_lua = dia.get("moon_phase", 0)

            if dado == "temperatura":
                resultado.append(f"{data}\n"
                                 f"🌡️ Manhã: {temperatura['morn']}°C\n" 
                                 f"🌡️ Tarde: {temperatura['day']}°C\n"
                                 f"🌙 Noite: {temperatura['night']}°C\n"
                                 f"🌙 Madrugada: {temperatura['eve']}°C\n"
                                 f"🌡️ Min: {temperatura['min']}°C\n"
                                 f"🌡️ Max: {temperatura['max']}°C\n"
                                 f"🥵 Sensação: Dia {sensacao['day']}°C\n"
                                 f"🥵 Noite {sensacao['night']}°C\n"
                                 f"☀️ UV: {uv}\n")

            elif dado == "chuva":
                resultado.append(f"{data}\n"
                                 f"🌧️ Probabilidade: {prob_chuva:.0f}%\n"
                                 f"🌦️ Volume: {volume_chuva} mm\n"
                                 f"❄️ Neve: {volume_neve} mm\n")

            elif dado == "vento":
                resultado.append(f"{data}\n"
                                 f"🌬️ Vento: {vento:.1f} km/h\n"
                                 f"🧭 Direção: {self.direcao_vento_em_texto(vento_dir)} ({vento_dir}°)\n"
                                 f"💨 Rajadas: {rajadas:.1f} km/h\n")

            elif dado == "clima":
                resultado.append(f"{data}\n"
                                 f"🌤️ Clima: {descricao}\n"
                                 f"☁️ Nuvens: {nuvens}%\n")

            elif dado == "umidade":
                resultado.append(f"{data}\n"
                                 f"💧 Umidade: {umidade}%\n")

            elif dado == "visibilidade":
                resultado.append(f"{data}\n"
                                 f"👁️ Visibilidade não disponível por dia na API.\n")

            elif dado == "pressao":
                resultado.append(f"{data}\n"
                                 f"🎚️ Pressão: {pressao} hPa\n")

            elif dado == "orvalho":
                resultado.append(f"{data}\n"
                                 f"🌫️ Ponto de orvalho: {orvalho}°C\n")

            elif dado == "lua":
                resultado.append(f"{data}\n"
                                 f"🌙 Nascer: {nascer_lua}"
                                 f"🌙 Pôr: {por_lua}\n"
                                 f"🌘 Fase da lua (0–1): {fase_lua:.2f}\n")

            else:
                resultado.append(f"\n📅 {data}\n"
                                 f"🌤️ Clima: {descricao}\n"
                                 f"🌡️ Manhã: {temperatura['morn']}°C\n"
                                 f"🌡️ Tarde: {temperatura['day']}°C\n"
                                 f"🌙 Noite: {temperatura['night']}°C" 
                                 f"🌙 Madrugada: {temperatura['eve']}°C\n"
                                 f"🌡️ Min: {temperatura['min']}°C\n"
                                 f"🌡️ Max: {temperatura['max']}°C\n"
                                 f"🥵 Sensação: Dia {sensacao['day']}°C\n"
                                 f"🥵 Sensação: Noite {sensacao['night']}°C\n"
                                 f"💧 Umidade: {umidade}%\n"
                                 f"☁️ Nuvens: {nuvens}%\n"
                                 f"🌬️ Vento: {vento:.1f} km/h\n"
                                 f"💨 Rajadas: {rajadas:.1f} km/h\n"
                                 f"🧭 Direção do vento: {self.direcao_vento_em_texto(vento_dir)} ({vento_dir}°)\n"
                                 f"🌧️ Prob. de chuva: {prob_chuva:.0f}%\n"
                                 f"🌦️ Volume: {volume_chuva} mm\n" 
                                 f"❄️ Neve: {volume_neve} mm\n"
                                 f"☀️ UV: {uv}\n" 
                                 f"🎚️ Pressão: {pressao} hPa\n" 
                                 f"🌫️ Orvalho: {orvalho}°C\n"
                                 f"🌅 Nascer do sol: {nascer_sol}\n"
                                 f"🌇 Pôr do sol: {por_sol}\n"
                                 f"🌙 Lua: nasce {nascer_lua}\n" 
                                 f"🌙 Lua: se põe {por_lua}\n"
                                 f"🌙 Fase {fase_lua:.2f}\n")

        texto_final = "\n".join(resultado)
        fala_final = f"Aqui está a previsão para os próximos {quantidade} dias."
        return texto_final, fala_final
