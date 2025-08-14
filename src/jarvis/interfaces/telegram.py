import telebot
import threading
from queue import Queue
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from core.locutor import carregar_locutor
from core.ouvido import transcrever_arquivo

class InterfaceTelegram:
    def __init__(self):
        load_dotenv()
        TOKEN = os.getenv("API_TELEGRAM")
        self.bot = telebot.TeleBot(TOKEN)
        self.fila = Queue()
        self.chat_id = None
        self.extensoes_imagem = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

        # Primeiro o handler de áudio
        @self.bot.message_handler(content_types=['voice', 'audio'])
        def receber_audio(msg):
            self.chat_id = msg.chat.id

            # Baixa o áudio do Telegram
            file_info = self.bot.get_file(msg.voice.file_id if msg.content_type == 'voice' else msg.audio.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            caminho_ogg = "temp_audio.ogg"
            with open(caminho_ogg, 'wb') as f:
                f.write(downloaded_file)

            # Converte para wav para melhorar precisão do reconhecimento
            caminho_wav = "temp_audio.wav"
            AudioSegment.from_file(caminho_ogg).export(caminho_wav, format="wav")

            # Transcreve e coloca na fila
            texto_transcrito = transcrever_arquivo(caminho_wav)
            self.fila.put(texto_transcrito)

            os.remove(caminho_ogg)
            os.remove(caminho_wav)

        @self.bot.message_handler(content_types=['photo', 'document'])
        def receber_imagem(msg):
            self.chat_id = msg.chat.id

            # Pega o arquivo (foto ou documento)
            if msg.content_type == 'photo':
                arquivo = msg.photo[-1]  # Maior resolução
            else:
                arquivo = msg.document

            file_info = self.bot.get_file(arquivo.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            # Define pasta temporária relativa ao arquivo atual
            base_dir = os.path.dirname(os.path.abspath(__file__))
            pasta_temp = os.path.join(base_dir, "img")
            os.makedirs(pasta_temp, exist_ok=True)

            # Caminho completo para salvar a imagem
            caminho_img = os.path.join(pasta_temp, "temp_imagem.jpg")
            with open(caminho_img, 'wb') as f:
                f.write(downloaded_file)

            # Pega a legenda (caption), se houver
            legenda = msg.caption or ""

            # Junta caminho da imagem + legenda em uma única string
            mensagem_final = f"{caminho_img} {legenda}".strip()

            # Envia para a fila
            self.fila.put(mensagem_final)

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

    def exibir_resposta(self, respostas):
        
        if self.chat_id:

            if not isinstance(respostas, list):
                respostas = [respostas]

            for resposta in respostas:

                if os.path.isfile(resposta) and resposta.lower().endswith(self.extensoes_imagem):
                    # Envia a imagem
                    with open(resposta, "rb") as img:
                        self.bot.send_photo(chat_id=self.chat_id, photo=img, caption="Aqui esta a imagem")

                else:    
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
