import os
import sqlite3
import requests
from datetime import datetime, timedelta, timezone
from time import sleep
from dotenv import load_dotenv
from modulos.base import ModuloBase
from core.interface import carregar_interface
from collections import Counter
from zoneinfo import ZoneInfo


class Historico(ModuloBase):
    def __init__(self):
        load_dotenv()
        self.interface = carregar_interface()
        self._token = os.getenv("API_CLIMA")
        self._lat = -31.31487713699913
        self._lon = -54.1174584168256
        self._db_path = "src/jarvis/data/clima.db"
        self.fuso_local = ZoneInfo("America/Sao_Paulo")  # Fuso fixo para o RS

    def extrair_parametros(self, frase: str) -> tuple[dict, dict]:
        parametros = {}
        faltando = {}
        return parametros, faltando

    def pegar_ultima_data_no_banco(self):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()
        cursor.execute("SELECT MAX(data) FROM clima_dia")
        resultado = cursor.fetchone()
        conexao.close()
        if resultado and resultado[0]:
            # Já salva como string 'YYYY-MM-DD', vamos garantir que seja timezone-aware local
            dt = datetime.strptime(resultado[0], "%Y-%m-%d")
            return dt.replace(tzinfo=self.fuso_local)
        else:
            # Data inicial padrão se banco vazio, ex: 7 dias atrás com fuso local
            return datetime.now(tz=self.fuso_local) - timedelta(days=7)

    def executar(self, **kwargs):
        self.interface.exibir_resposta("Iniciando coleta do histórico incremental...")

        ultima_data = self.pegar_ultima_data_no_banco()
        data_inicial = ultima_data + timedelta(days=1)  # Próximo dia depois da última
        data_final = datetime.now(tz=self.fuso_local) - timedelta(days=1)  # Ontem no horário local

        print(f"Ultima data {ultima_data}")
        print(f"Data Inicial {data_inicial}")
        print(f"Data Final {data_final}")

        if data_inicial > data_final:
            self.interface.exibir_resposta("Banco já atualizado até ontem.")
            return "Nada novo para coletar", "Nada novo para coletar"

        registros = []

        data_atual = data_inicial
        while data_atual <= data_final:
            data_str = data_atual.strftime('%Y-%m-%d')
            self.interface.exibir_resposta(f"Coletando dados para {data_str}...")

            for hora in range(24):
                # cria datetime no horário local para a hora
                dt_local = datetime(
                    data_atual.year,
                    data_atual.month,
                    data_atual.day,
                    hour=hora,
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=self.fuso_local
                )
                # converte para UTC para gerar timestamp que a API espera
                dt_utc = dt_local.astimezone(timezone.utc)
                timestamp = int(dt_utc.timestamp())

                if self.verificar_existencia_timestamp(timestamp):
                    self.interface.exibir_resposta(f"{dt_utc} já existe no banco. Pulando.")
                    continue

                print(dt_utc)
                print(timestamp)
                # input("parou")  # pode remover depois que confirmar que está ok

                url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
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
                        print(f"[Jarvis] Resposta inesperada para hora {hora} em {data_str}")
                else:
                    print(f"[Jarvis] Erro: {resposta.status_code} - {resposta.text}")
                sleep(1.2)

            data_atual += timedelta(days=1)

        if registros:
            self.inserir_dados_horarios(registros)
            # Gerar resumo para todos os dias coletados
            data_temp = data_inicial
            while data_temp <= data_final:
                self.gerar_resumo_dia(data_temp.strftime('%Y-%m-%d'))
                data_temp += timedelta(days=1)

            print("[Jarvis] Coleta e inserção concluídas com sucesso.")
            return "Coleta completa", "Coleta completa"
        else:
            print("[Jarvis] Nenhum dado coletado.")
            return "Nenhum dado coletado", "Nenhum dado coletado"

    def verificar_existencia_timestamp(self, timestamp):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM clima_hora WHERE timestamp_utc = ?", (timestamp,))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado is not None

    def inserir_dados_horarios(self, lista_dados, origem="api"):
        conexao = sqlite3.connect(self._db_path)
        cursor = conexao.cursor()

        for hora in lista_dados:
            timestamp = hora.get("dt")
            # Converte timestamp UTC para horário local antes de formatar string
            data_local = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(self.fuso_local).strftime('%Y-%m-%d %H:%M:%S')

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
                INSERT INTO clima_hora (
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
            SELECT temp, feels_like, pressure, humidity, dew_point, uvi, clouds, visibility,
                wind_speed, wind_deg, wind_gust, weather_description ,rain_1h, snow_1h
            FROM clima_hora 
            WHERE data_local LIKE ?
        """, (f"{data_str}%",))
        registros = cursor.fetchall()

        if not registros:
            print(f"Nenhum dado horário encontrado para {data_str}")
            return

        def min_max_med(lista):
            return (min(lista), max(lista), sum(lista)/len(lista)) if lista else (None, None, None)

        def graus_para_direcao(graus):
            direcoes = ['Norte', 'Nordeste', 'Leste', 'Sudeste', 'Sul', 'Sudoeste', 'Oeste', 'Noroeste']
            ix = int((graus + 22.5) / 45) % 8
            return direcoes[ix]

        # Extrair colunas ignorando None
        temp = [r[0] for r in registros if r[0] is not None]
        feels_like = [r[1] for r in registros if r[1] is not None]
        pressure = [r[2] for r in registros if r[2] is not None]
        humidity = [r[3] for r in registros if r[3] is not None]
        dew_point = [r[4] for r in registros if r[4] is not None]
        uvi = [r[5] for r in registros if r[5] is not None]
        clouds = [r[6] for r in registros if r[6] is not None]
        visibility = [r[7] for r in registros if r[7] is not None]
        wind_speed = [r[8] for r in registros if r[8] is not None]
        wind_deg = [r[9] for r in registros if r[9] is not None]
        wind_gust = [r[10] for r in registros if r[10] is not None]
        weather_description = [r[11] for r in registros if r[11] is not None]
        rain_1h = [r[12] for r in registros if r[12] is not None]
        snow_1h = [r[13] for r in registros if r[13] is not None]

        temp_min, temp_max, temp_med = min_max_med(temp)
        sens_min, sens_max, sens_med = min_max_med(feels_like)
        press_min, press_max, press_med = min_max_med(pressure)
        umid_min, umid_max, umid_med = min_max_med(humidity)
        orv_min, orv_max, orv_med = min_max_med(dew_point)
        uvi_min, uvi_max, uvi_med = min_max_med(uvi)
        nuv_min, nuv_max, nuv_med = min_max_med(clouds)
        vis_min, vis_max, vis_med = min_max_med(visibility)
        vent_min, vent_max, vent_med = min_max_med(wind_speed)

        # Direção predominante do vento no dia
        direcoes_convertidas = [graus_para_direcao(g) for g in wind_deg]
        if direcoes_convertidas:
            direcao_predominante = Counter(direcoes_convertidas).most_common(1)[0][0]
        else:
            direcao_predominante = None

        raj_min, raj_max, raj_med = min_max_med(wind_gust)

        if weather_description:
            clima_predominante = Counter(weather_description).most_common(1)[0][0]
        else:
            clima_predominante = None

        chuva_total = sum(rain_1h) if rain_1h else 0
        neve_total = sum(snow_1h) if snow_1h else 0

        cursor.execute("SELECT id FROM clima_dia WHERE data = ?", (data_str,))
        if cursor.fetchone():
            print(f"Resumo de {data_str} já existe. Pulando.")
        else:
            cursor.execute("""
                INSERT INTO clima_dia (
                    data,
                    temperatura_min, temperatura_max, temperatura_media,
                    sensacao_min, sensacao_max, sensacao_media,
                    pressao_min, pressao_max, pressao_media,
                    umidade_min, umidade_max, umidade_media,
                    orvalho_min, orvalho_max, orvalho_media,
                    uvi_min, uvi_max, uvi_media,
                    nuvens_min, nuvens_max, nuvens_media,
                    visibilidade_min, visibilidade_max, visibilidade_media,
                    vento_min, vento_max, vento_media,
                    rajada_min, rajada_max, rajada_media,
                    direcao_predominante,
                    precipitacao_total, neve_total,
                    clima_predominante,
                    origem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_str,
                temp_min, temp_max, temp_med,
                sens_min, sens_max, sens_med,
                press_min, press_max, press_med,
                umid_min, umid_max, umid_med,
                orv_min, orv_max, orv_med,
                uvi_min, uvi_max, uvi_med,
                nuv_min, nuv_max, nuv_med,
                vis_min, vis_max, vis_med,
                vent_min, vent_max, vent_med,
                raj_min, raj_max, raj_med,
                direcao_predominante,
                chuva_total, neve_total,
                clima_predominante,
                "api"
            ))
            conexao.commit()
            print(f"Resumo para {data_str} inserido.")
