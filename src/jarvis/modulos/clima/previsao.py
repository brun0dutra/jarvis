from modulos.base import ModuloBase
from dotenv import load_dotenv
import requests
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from statistics import mean

class Previsao(ModuloBase):
    def __init__(self):
        load_dotenv()
        self._token = os.getenv("API_CLIMA")
        self._cidade = "Bagé"
        self._link = f"https://api.openweathermap.org/data/2.5/forecast?q={self._cidade}&appid={self._token}&lang=pt_br&units=metric"

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        numeros = list(map(int, re.findall(r"\d+", frase)))
        parametros = {}
        faltando = {}

        if len(numeros) >= 1:
            parametros["dias"] = numeros[0]
        
        return parametros, faltando
    
    def executar(self, **kwargs):

        dias = int(kwargs.get("dias", 5))

        def direcao_vento_em_texto(graus):
            direcoes = [
                "Norte", "Nordeste", "Leste", "Sudeste",
                "Sul", "Sudoeste", "Oeste", "Noroeste"
            ]
            index = int((graus + 22.5) // 45) % 8
            return direcoes[index]

        def dia_semana_em_portugues(data_str):
            dias_semana = {
                "Monday": "Segunda-feira",
                "Tuesday": "Terça-feira",
                "Wednesday": "Quarta-feira",
                "Thursday": "Quinta-feira",
                "Friday": "Sexta-feira",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            dia_semana_en = datetime.strptime(data_str, "%Y-%m-%d").strftime("%A")
            data_formatada = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m")
            return f"{dias_semana[dia_semana_en]}, {data_formatada}"

    
        link = f"https://api.openweathermap.org/data/2.5/forecast?q={self._cidade}&appid={self._token}&lang=pt_br&units=metric"
        resposta = requests.get(link)
        dados = resposta.json()

        previsoes_por_dia = defaultdict(list)
        for item in dados['list']:
            data = item['dt_txt'].split(' ')[0]
            previsoes_por_dia[data].append(item)

        texto_final = ""
        fala_final = ""

        dias_processados = 0
        for data, previsoes in previsoes_por_dia.items():
            if dias_processados >= dias:
                break

            dia = dia_semana_em_portugues(data)

            temperaturas = [p['main']['temp'] for p in previsoes]
            sensacoes = [p['main']['feels_like'] for p in previsoes]
            temp_min = min(p['main']['temp_min'] for p in previsoes)
            temp_max = max(p['main']['temp_max'] for p in previsoes)
            umidades = [p['main']['humidity'] for p in previsoes]
            nuvens = [p['clouds']['all'] for p in previsoes]
            pressoes = [p['main']['pressure'] for p in previsoes]
            visibilidades = [p.get('visibility', 10000) / 1000 for p in previsoes]
            velocidades_vento = [p['wind']['speed'] * 3.6 for p in previsoes]
            direcoes_vento = [p['wind']['deg'] for p in previsoes]
            rajadas_vento = [p['wind'].get('gust', 0) * 3.6 for p in previsoes]
            descricoes = [p['weather'][0]['description'] for p in previsoes]
            chuva_total = sum(p.get('rain', {}).get('3h', 0) for p in previsoes)

            direcao_media = mean(direcoes_vento)
            texto_direcao = direcao_vento_em_texto(direcao_media)

            texto_final += (
                f"📅 {dia}\n"
                f"🌡 Atual (média): {mean(temperaturas):.1f}°C | Sensação: {mean(sensacoes):.1f}°C\n"
                f"🌡 Mín: {temp_min:.1f}°C | Máx: {temp_max:.1f}°C\n"
                f"💧 Umidade: {mean(umidades):.0f}% | ☁️ Nuvens: {mean(nuvens):.0f}%\n"
                f"🧭 Vento médio: {mean(velocidades_vento):.1f} km/h | Vindo do: {texto_direcao} ({direcao_media:.0f}°) | Rajadas: {mean(rajadas_vento):.1f} km/h\n"
                f"🌫 Visibilidade média: {mean(visibilidades):.1f} km | 🔽 Pressão: {mean(pressoes):.0f} hPa\n"
                f"🌤 Tempo: {Counter(descricoes).most_common(1)[0][0]}\n"
                f"🌧 Chuva total: {chuva_total:.1f} mm\n"
                f"{'-' * 40}\n"
            )

            fala_final += (
                f"{dia}, teremos {Counter(descricoes).most_common(1)[0][0]}, com"
                f"maxima de {temp_max:.1f}°C, e minima de {temp_min:.1f}°C"
            )

            dias_processados += 1

        return texto_final, fala_final
