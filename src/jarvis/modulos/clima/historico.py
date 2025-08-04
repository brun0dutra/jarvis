import os
import sqlite3
import requests
from datetime import datetime, timedelta
from time import sleep
from dotenv import load_dotenv
from modulos.base import ModuloBase
from core.interface import carregar_interface


class Historico(ModuloBase):
    def __init__(self):
        load_dotenv()
        self.interface = carregar_interface()
        self._token = os.getenv("API_CLIMA")
        self._lat = -31.31487713699913
        self._lon = -54.1174584168256
        self._db_path = "src/jarvis/data/clima.db"

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        parametros = {}
        faltando = {}
        
        return parametros, faltando

    def executar(self, **kwargs):
        self.interface.exibir_resposta("Iniciando coleta do histórico de ontem...")
        ontem = datetime.utcnow() - timedelta(days=1)
        data_str = ontem.strftime('%Y-%m-%d')
        registros = []

        for hora in range(24):
            dt_obj = ontem.replace(hour=hora, minute=0, second=0, microsecond=0)
            timestamp = int(dt_obj.timestamp())

            if self.verificar_existencia_timestamp(timestamp):
                self.interface.exibir_resposta(f"{dt_obj} já existe no banco. Pulando.")
                continue

            url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
            params = {
                "lat": self._lat,
                "lon": self._lon,
                "dt": timestamp,
                "appid": self._token,
                "units": "metric",
                "lang": "pt_br"
            }

            resposta = requests.get(url, params=params)

            if resposta.status_code == 200:
                json_data = resposta.json()
                if "data" in json_data and isinstance(json_data["data"], list):
                    registros.extend(json_data["data"])
                else:
                    print(f"[Jarvis] Resposta inesperada para hora {hora}")
            else:
                print(f"[Jarvis] Erro: {resposta.status_code} - {resposta.text}")
            sleep(1.2)

        if registros:
            self.inserir_dados_horarios(registros)
            self.gerar_resumo_dia(data_str)
            print("[Jarvis] Coleta e inserção concluídas com sucesso.")
            return "teste", "teste"
        else:
            print("[Jarvis] Nenhum dado coletado.")
            return "Nenhum dado coletado", "Nenhum dado coletado"

    def verificar_existencia_timestamp(self, timestamp):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM clima_horario WHERE timestamp_utc = ?", (timestamp,))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado is not None

    def inserir_dados_horarios(self, lista_dados, origem="api"):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()

        for hora in lista_dados:
            timestamp = hora.get("dt")
            data_local = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            temp = hora.get("temp")
            feels_like = hora.get("feels_like")
            pressure = hora.get("pressure")
            humidity = hora.get("humidity")
            dew_point = hora.get("dew_point")
            uvi = hora.get("uvi")
            clouds = hora.get("clouds")
            visibility = hora.get("visibility")
            wind_speed = hora.get("wind_speed")
            wind_deg = hora.get("wind_deg")
            wind_gust = hora.get("wind_gust")
            pop = hora.get("pop", 0)
            rain_1h = hora.get("rain", {}).get("1h", 0)
            snow_1h = hora.get("snow", {}).get("1h", 0)

            weather_main = None
            weather_description = None
            weather_icon = None
            if "weather" in hora and len(hora["weather"]) > 0:
                weather_main = hora["weather"][0].get("main")
                weather_description = hora["weather"][0].get("description")
                weather_icon = hora["weather"][0].get("icon")

            cursor.execute("""
                INSERT INTO clima_horario (
                    timestamp_utc, data_local, temp, feels_like, pressure, humidity,
                    dew_point, uvi, clouds, visibility, wind_speed, wind_deg, wind_gust,
                    weather_main, weather_description, weather_icon, pop, rain_1h, snow_1h, origem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                data_local,
                temp,
                feels_like,
                pressure,
                humidity,
                dew_point,
                uvi,
                clouds,
                visibility,
                wind_speed,
                wind_deg,
                wind_gust,
                weather_main,
                weather_description,
                weather_icon,
                pop,
                rain_1h,
                snow_1h,
                origem
            ))

        conexao.commit()
        conexao.close()

    def gerar_resumo_dia(self, data_str):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT temp, humidity, wind_speed, rain_1h FROM clima_horario 
            WHERE data_local LIKE ?
        """, (f"{data_str}%",))
        registros = cursor.fetchall()

        if not registros:
            print(f"[Jarvis] Nenhum dado horário encontrado para {data_str}")
            conexao.close()
            return

        temps = [r[0] for r in registros if r[0] is not None]
        hums = [r[1] for r in registros if r[1] is not None]
        vents = [r[2] for r in registros if r[2] is not None]
        chuvas = [r[3] for r in registros if r[3] is not None]

        temp_min = min(temps)
        temp_max = max(temps)
        temp_med = sum(temps) / len(temps)
        hum_med = sum(hums) / len(hums)
        vent_med = sum(vents) / len(vents)
        chuva_total = sum(chuvas)

        cursor.execute("SELECT id FROM clima_diario WHERE data = ?", (data_str,))
        if cursor.fetchone():
            print(f"[Jarvis] Resumo de {data_str} já existe. Pulando.")
        else:
            cursor.execute("""
                INSERT INTO clima_diario 
                (data, temp_min, temp_max, temp_media, umidade_media, vento_medio, precipitacao_total, origem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_str,
                temp_min,
                temp_max,
                temp_med,
                hum_med,
                vent_med,
                chuva_total,
                "api"
            ))

        conexao.commit()
        conexao.close()
