from modulos.base import ModuloBase
from dotenv import load_dotenv
import requests
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from statistics import mean

class Previsaohora(ModuloBase):
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

        # Tenta extrair o número de horas com regex
        match = re.search(r"(\d{1,2})\s*(h|horas)?", frase)
        if match:
            qtd = int(match.group(1))
            parametros["quantidade_horas"] = max(1, min(qtd, 48))
        else:
            parametros["quantidade_horas"] = 24

        intencoes = {
            "temperatura": ["temperatura", "calor", "frio", "sensação", "termica", "indici uv", "raios uv", "raios do sol", "sol"],
            "chuva": ["chuva", "chover", "precipitação", "probabilidade", "volume", "milimetros"],
            "umidade": ["umidade", "úmido", "seco"],
            "vento": ["vento", "ventania", "ventar", "velocidade", "rajadas", "direção", "direção do vento"],
            "clima": ["clima", "tempo", "condição", "nuvens", "nuvem"],
            "visibilidade": ["visibilidade", "visão", "nevoeiro", "nevoa", "serração"],
            "pressao": ["pressao", "atmosferica", "pressao atmosferica"],
            "orvalho": ["ponto", "orvalho", "ponto do orvalho"]
        }

        for chave, palavras in intencoes.items():
            if any(p in frase for p in palavras):
                parametros["dado"] = chave
                break

        return parametros, faltando

    def direcao_vento_em_texto(self, graus):
        direcoes = [
            "Norte", "Nordeste", "Leste", "Sudeste",
            "Sul", "Sudoeste", "Oeste", "Noroeste"
        ]
        index = int((graus + 22.5) // 45) % 8
        return direcoes[index]

    def executar(self, **kwargs):
        dados = requests.get(self._link).json()
        timezone_offset = dados["timezone_offset"]
        horas = dados["hourly"]
        quantidade = kwargs.get("quantidade_horas", 48)
        dado = kwargs.get("dado")

        resultado = []

        for hora in horas[:quantidade]:
            horario = (datetime.utcfromtimestamp(hora["dt"]) + timedelta(seconds=timezone_offset)).strftime("%d/%m %H:%M")

            # Dados brutos
            descricao = hora['weather'][0]['description'].capitalize()
            temperatura = hora['temp']
            sensacao = hora['feels_like']
            umidade = hora['humidity']
            vento_vel = hora['wind_speed'] * 3.6
            vento_dir = hora['wind_deg']
            rajadas = hora.get('wind_gust', 0) * 3.6
            nuvens = hora['clouds']
            prob_chuva = hora.get('pop', 0) * 100
            volume_chuva = hora.get('rain', {}).get('1h', 0)
            visibilidade = hora.get('visibility', 0) / 1000
            uv = hora.get('uvi', 0)
            pressao = hora.get('pressure', 0)
            orvalho = hora.get('dew_point', 0)

            # Apenas o dado específico
            if dado == "clima":
                resultado.append(f"{horario}\n"
                                 f"🌤️ Clima: {descricao}\n"
                                 f"☁️ Nuvens: {nuvens}% \n"
                                 "\n")

            elif dado == "temperatura":
                resultado.append(f"{horario}\n"
                                 f"🌡️ Temperatura: {temperatura:.1f}°C\n"
                                 f"🌡️ Sensação Termica: {sensacao}°C\n"
                                 f"☀️ Índice UV: {uv}\n"
                                 "\n")

            elif dado == "chuva":
                resultado.append(f"{horario}\n"
                                 f"☁️ Nuvens: {nuvens}% \n"
                                 f"🌧️ Probabilidade: {prob_chuva:.0f}%\n"
                                 f"🌦️ Volume: {volume_chuva} mm\n"
                                 "\n")


            elif dado == "umidade":
                resultado.append(f"{horario}\n"
                                 f"💧 Umidade: {umidade}%\n"
                                 "\n")


            elif dado == "vento":
                resultado.append(f"{horario}\n"
                                 f"🌬️ Velocidade: {vento_vel:.1f} km/h\n"
                                 f"🧭 Direção: {self.direcao_vento_em_texto(vento_dir)}\n"
                                 f"💨 Rajadas: {rajadas:.1f} km/h\n"
                                 "\n")
                
            elif dado == "visibilidade":
                resultado.append(f"{horario}\n"
                                 f"👁️ Visibilidade: {visibilidade} km\n"
                                 "\n")
                
            elif dado == "pressao":
                resultado.append(f"{horario}\n"
                                 f"Pressão Atmosferica: {pressao}hPa\n"
                                 "\n")
                
            elif dado == "orvalho":
                resultado.append(f"{horario}\n"
                                 f"🌫️ Ponto de orvalho: {orvalho}°C\n"
                                 "\n")

            else:
                # Todos os dados, formatados como no texto_final
                resultado.append(
                    f"\n🕒 Horário: {horario}\n"
                    f"🌤️ Clima: {descricao}\n"
                    f"🌡️ Temperatura: {temperatura}°C\n"
                    f"🌡️ Sensação térmica: {sensacao}°C\n"
                    f"💧 Umidade: {umidade}%\n"
                    f"🌬️ Velocidade do vento: {vento_vel:.1f} km/h\n"
                    f"🧭 Direção do vento: {self.direcao_vento_em_texto(vento_dir)} ({vento_dir}°)\n"
                    f"💨 Rajadas de vento: {rajadas:.1f} km/h\n"
                    f"☁️ Nuvens: {nuvens}%\n"
                    f"🌧️ Probabilidade de chuva: {prob_chuva:.0f}%\n"
                    f"🌦️ Volume de chuva: {volume_chuva} mm\n"
                    f"👁️ Visibilidade: {visibilidade:.1f} km\n"
                    f"☀️ Índice UV: {uv}\n"
                    f"🎚️ Pressão atmosférica: {pressao} hPa\n"
                    f"🌫️ Ponto de orvalho: {orvalho}°C\n"
                )

        texto_final = "\n".join(resultado)
        fala_final = f"Aqui está a previsão para as próximas {quantidade} horas."
        return texto_final, fala_final
