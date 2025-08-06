import telebot
import threading
from queue import Queue
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from core.locutor import carregar_locutor

class InterfaceTelegram:
    def __init__(self):
        load_dotenv()
        TOKEN = os.getenv("API_TELEGRAM")
        self.bot = telebot.TeleBot(TOKEN)
        self.fila = Queue()
        self.chat_id = None

        @self.bot.message_handler(func=lambda msg: True)
        def receber(msg):
            self.chat_id = msg.chat.id
            self.fila.put(msg.text)

        # Inicia o bot em segundo plano
        threading.Thread(target=self.bot.infinity_polling, daemon=True).start()

    def receber_entrada(self, pergunta=None):
        if pergunta:
            self.exibir_resposta(pergunta)

        # Espera até uma nova mensagem ser recebida
        texto = self.fila.get()
        return texto

    def exibir_resposta(self, resposta):
        if self.chat_id:
            self.bot.send_message(self.chat_id, resposta)

    def falar_resposta(self, resposta):
        
        def converter_para_ogg(caminho_mp3: str) -> str:
            caminho_ogg = caminho_mp3.replace(".mp3", ".ogg")
            AudioSegment.from_mp3(caminho_mp3).export(caminho_ogg, format="ogg", codec="libopus")
            return caminho_ogg

        locutor = carregar_locutor()
        caminho_do_auido = locutor(resposta)
        caminho_ogg = converter_para_ogg(caminho_do_auido)        

        try:
            with open(caminho_ogg, 'rb') as audio:
                    self.bot.send_voice(chat_id=self.chat_id, voice=audio)
        finally:
            if caminho_do_auido:
                os.remove(caminho_do_auido)
            if caminho_ogg:
                os.remove(caminho_ogg)
