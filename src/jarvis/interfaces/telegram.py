import telebot
import threading
from queue import Queue
import os
from dotenv import load_dotenv

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
