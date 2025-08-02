import requests
import os
from datetime import datetime, timedelta
from modulos.base import ModuloBase
from dotenv import load_dotenv

class ClimaAntigo(ModuloBase):
    def __init__(self):
        load_dotenv()
        TOKEN = os.getenv("API_CLIMA")
        self._api =  TOKEN
        self._cidade = "Bagé"
        self._link = f"https://api.openweathermap.org/data/2.5/weather?q={self._cidade}&appid={self._api}&lang=pt_br"
        
        self.cidade = ""
        self.pais = ""
        self.clima = ""
        self.temperatura = ""

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        parametros = {}
        faltando = {}

        return parametros, faltando

    def executar(self):
        dados = requests.get(self._link).json()

        def kelvin_para_celsius(k):
            return round(k - 273.15, 1)

        # Função para converter timestamp UNIX para hora local
        def timestamp_para_hora(timestamp, timezone_offset):
            return (datetime.utcfromtimestamp(timestamp) + timedelta(seconds=timezone_offset)).strftime('%H:%M:%S')

        def grau_para_direcao(deg):
            direcoes = ['Norte', 'NE', 'E', 'SE', 'Sul', 'SW', 'W', 'NW']
            indice = int((deg + 22.5) % 360 / 45)
            return direcoes[indice]


        self.cidade = dados.get("name")
        self.pais = dados["sys"].get("country")
        self.clima = dados["weather"][0]["description"].capitalize()
        self.temperatura = kelvin_para_celsius(dados["main"]["temp"])
        self.sensacao = kelvin_para_celsius(dados["main"]["feels_like"])
        self.temp_min = kelvin_para_celsius(dados["main"]["temp_min"])
        self.temp_max = kelvin_para_celsius(dados["main"]["temp_max"])
        self.umidade = dados["main"]["humidity"]
        self.pressao = dados["main"]["pressure"]
        self.vento_vel = round(dados["wind"]["speed"] * 3.6, 1)  # m/s para km/h
        self.vento_dir = grau_para_direcao(dados["wind"]["deg"])
        self.nuvens = dados["clouds"]["all"]
        self.visibilidade = dados["visibility"] / 1000  # metros para km
        self.nascer_sol = timestamp_para_hora(dados["sys"]["sunrise"], dados["timezone"])
        self.por_sol = timestamp_para_hora(dados["sys"]["sunset"], dados["timezone"])
        self.horario_atual = timestamp_para_hora(dados["dt"], dados["timezone"])

        resposta = (
            f"📍 Clima em {self.cidade}, {self.pais}\n"
            f"🕒 Última atualização: {self.horario_atual}\n"
            f"🌤️ Condição: {self.clima}\n"
            f"🌡️ Temperatura: {self.temperatura}°C (Sensação térmica: {self.sensacao}°C)\n"
            f"🔺 Máx: {self.temp_max}°C | 🔻 Mín: {self.temp_min}°C\n"
            f"💧 Umidade: {self.umidade}%"
            f"🌬️ Vento: {self.vento_vel} km/h (Direção: {self.vento_dir}°)\n"
            f"🔎 Visibilidade: {self.visibilidade} km\n"
            f"☁️ Cobertura de nuvens: {self.nuvens}%\n"
            f"📈 Pressão atmosférica: {self.pressao} hPa\n"
            f"🌅 Nascer do sol: {self.nascer_sol}\n"
            f"🌇 Pôr do sol: {self.por_sol}\n"
        )

        fala = (
            f"Na cidade de {self.cidade} temos {self.clima},\n "
        f"com temperatura de {self.temperatura} graus, e sensassão termica de {self.sensacao} graus.\n "
        f"A umidade esta em {self.umidade}%. Temos ventos vindo do {self.vento_dir}, a {self.vento_vel} Km/h.\n "
        f"Céu esta {self.nuvens}% coberto de nuvens). A sua visibilidade é de {self.visibilidade} Km.\n "
        f"Nascer do sol as {self.nascer_sol}, e o por do sol as {self.por_sol}\n")

        return resposta, fala
    
class Clima(ModuloBase):
    def __init__(self):
        load_dotenv()
        self._token = os.getenv("API_CLIMA")
        self._lat = -31.31487713699913
        self._lon = -54.1174584168256
        self._link = f"https://api.openweathermap.org/data/3.0/onecall?lat={self._lat}&lon={self._lon}&appid={self._token}&units=metric&lang=pt_br"

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
            intencoes = {
            "temperatura": ["temperatura", "graus", "calor", "frio", "termômetro"],
            "chuva": ["chuva", "vai chover", "precipitação"],
            "vento": ["vento", "rajadas", "soprando", "ventania"],
            "umidade": ["umidade", "úmido", "seco"],
            "uv": ["índice uv", "uv", "raios ultravioleta"],
            "visibilidade": ["visibilidade", "enxergar", "neblina"],
            "pressao": ["pressão", "barômetro"],
            "nuvens": ["nuvens", "nublado", "céu"],
            "ponto_orvalho": ["ponto de orvalho", "orvalho", "condensação"],
            "nascer_por": ["nascer do sol", "pôr do sol", "amanhecer", "anoitecer"],
            "completo": ["clima", "tempo", "atualização", "situação geral", "como está"]
        }

            for chave, palavras in intencoes.items():
                if any(p in frase.lower() for p in palavras):
                    return {"dado": chave}, {}

                return {"dado": "completo"}, {}
    
    def executar(self, **kwargs):
        dados = requests.get(self._link).json()
        atual = dados["current"]
        previsao_hoje = dados["daily"][0]

        def timestamp_para_hora(timestamp, timezone_offset):
            return (datetime.utcfromtimestamp(timestamp) + timedelta(seconds=timezone_offset)).strftime('%H:%M:%S')

        def direcao_vento_em_texto(graus):
            direcoes = [
                "Norte", "Nordeste", "Leste", "Sudeste",
                "Sul", "Sudoeste", "Oeste", "Noroeste"
            ]
            index = int((graus + 22.5) // 45) % 8
            return direcoes[index]

        dado = kwargs.get("dado", "completo")

        horario_atual = timestamp_para_hora(atual["dt"], dados["timezone_offset"])
        descricao = atual["weather"][0]["description"].capitalize()
        temperatura = atual["temp"]
        sensacao = atual["feels_like"]
        temp_minima = previsao_hoje["temp"]["min"]
        temp_maxima = previsao_hoje["temp"]["max"]
        umidade = atual["humidity"]
        vento_vel = atual["wind_speed"] * 3.6
        vento_dir = atual["wind_deg"]
        vento_raj = previsao_hoje.get("wind_gust", 0) * 3.6  # Convertendo para km/h
        nuvens = atual["clouds"]
        prob_chuva = previsao_hoje.get("pop", 0) * 100  # valor entre 0 e 1 → %
        chuva = previsao_hoje.get("rain", 0)  # em mm
        visibilidade = atual["visibility"] / 1000
        uv = atual["uvi"]
        pressao = atual["pressure"]
        ponto_orvalho = atual["dew_point"]
        nascer_sol = timestamp_para_hora(atual["sunrise"], dados["timezone_offset"])
        por_sol = timestamp_para_hora(atual["sunset"], dados["timezone_offset"])

        # Respostas específicas
        if dado == "temperatura":
            return (
                f"🌡️ Temperatura atual: {temperatura}°C\n"
                f"🌡️ Sensação térmica: {sensacao}°C\n"
                f"🔺 Máxima: {temp_maxima}°C | 🔻 Mínima: {temp_minima}°C\n",
                f"A temperatura atual é de {temperatura} graus, com sensação de {sensacao}. Mínima de {temp_minima} e máxima de {temp_maxima} graus."
            )

        elif dado == "chuva":
            return (
                f"🌧️ Probabilidade de chuva: {prob_chuva:.0f}%\n"
                f"🌦️ Volume de chuva: {chuva} mm\n",
                f"A chance de chover hoje é de {prob_chuva:.0f}%, com previsão de {chuva} milímetros."
            )

        elif dado == "vento":
            return (
                f"🌬️ Velocidade do vento: {vento_vel:.1f} km/h\n"
                f"🧭 Direção: {direcao_vento_em_texto(vento_dir)} ({vento_dir}°)\n"
                f"💨 Rajadas: {vento_raj:.1f} km/h\n",
                f"O vento está a {vento_vel:.1f} km/h, vindo do {direcao_vento_em_texto(vento_dir)}. Rajadas de até {vento_raj:.1f} km/h."
            )

        elif dado == "umidade":
            return (
                f"💧 Umidade relativa do ar: {umidade}%\n",
                f"A umidade atual está em {umidade} por cento."
            )

        elif dado == "uv":
            return (
                f"☀️ Índice UV: {uv}\n",
                f"O índice UV atual está em {uv}."
            )

        elif dado == "visibilidade":
            return (
                f"👁️ Visibilidade: {visibilidade:.1f} km\n",
                f"A visibilidade é de {visibilidade:.1f} quilômetros."
            )

        elif dado == "pressao":
            return (
                f"🎚️ Pressão atmosférica: {pressao} hPa\n",
                f"A pressão atmosférica está em {pressao} hectopascais."
            )

        elif dado == "nuvens":
            return (
                f"☁️ Cobertura de nuvens: {nuvens}%\n",
                f"O céu está com {nuvens}% de nuvens."
            )

        elif dado == "ponto_orvalho":
            return (
                f"🌫️ Ponto de orvalho: {ponto_orvalho}°C\n",
                f"O ponto de orvalho está em {ponto_orvalho} graus Celsius."
            )

        elif dado == "nascer_por":
            return (
                f"🌄 Nascer do sol: {nascer_sol}\n"
                f"🌇 Pôr do sol: {por_sol}\n",
                f"O sol nasce às {nascer_sol} e se põe às {por_sol}."
            )

        else:  # Caso padrão: clima completo
            texto_final = (
                f"\n🕒 Horario: {horario_atual}\n"
                f"🌤️ Clima: {descricao}\n"
                f"🌡️ Temperatura: {temperatura}°C\n"
                f"🌡️ Sensação térmica: {sensacao}°C\n"
                f"🔻 Temperatura Mínima: {temp_minima}°C\n"
                f"🔺 Temperatura Máxima: {temp_maxima}°C\n"
                f"💧 Umidade: {umidade}%\n"
                f"🌬️ Velocidade do vento: {vento_vel:.1f} km/h\n"
                f"🧭 Direção do vento: {direcao_vento_em_texto(vento_dir)} ({vento_dir}°)\n"
                f"💨 Rajadas de vento: {vento_raj:.1f} km/h\n"
                f"☁️ Nuvens: {nuvens}%\n"
                f"🌧️ Probabilidade de chuva: {prob_chuva:.0f}%\n"
                f"🌦️ Volume de chuva: {chuva} mm\n"
                f"👁️ Visibilidade: {visibilidade:.1f} km\n"
                f"☀️ Índice UV: {uv}\n"
                f"🎚️ Pressão atmosférica: {pressao} hPa\n"
                f"🌫️ Ponto de orvalho: {ponto_orvalho}°C\n"
                f"🌄 Nascer do sol: {nascer_sol}\n"
                f"🌇 Pôr do sol: {por_sol}\n"
            )

            fala_final = (
                f"Temos {descricao}. Temperatura de {temperatura:.1f} graus, sensação térmica de {sensacao:.1f}, mínima de {temp_minima:.1f} e máxima de {temp_maxima:.1f}. "
                f"Ventos a {vento_vel:.1f} km/h vindos de {direcao_vento_em_texto(vento_dir)}. "
                f"Chance de chuva: {prob_chuva:.0f}%. Índice UV: {uv}. O sol nasce às {nascer_sol} e se põe às {por_sol}."
            )

            return texto_final, fala_final
        
