import speech_recognition as sr

def escutar_ate_parar():
    reconhecedor = sr.Recognizer()
    with sr.Microphone() as fonte:
        print("🎙️ Fale alguma coisa (vou detectar quando você parar)...")
        audio = reconhecedor.listen(fonte)  # Espera até você parar de falar
        try:
            texto = reconhecedor.recognize_google(audio, language="pt-BR")
            return texto
        except sr.UnknownValueError:
            return "Não entendi."
        except sr.RequestError:
            return "Erro no serviço de voz."
        
def transcrever_arquivo(caminho_audio):
    reconhecedor = sr.Recognizer()
    with sr.AudioFile(caminho_audio) as fonte:
        audio = reconhecedor.record(fonte)
        try:
            texto = reconhecedor.recognize_google(audio, language="pt-BR")
            return texto
        except sr.UnknownValueError:
            return "Não entendi."
        except sr.RequestError:
            return "Erro no serviço de voz."
