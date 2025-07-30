import requests
import os
from datetime import datetime, timedelta
from modulos.base import ModuloBase
from dotenv import load_dotenv

class Clima(ModuloBase):
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