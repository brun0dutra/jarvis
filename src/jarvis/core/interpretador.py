from config.setting import CONFIG

def carregar_motor():
    tipo = CONFIG.get("motor_interpretacao")

    if tipo == "tfidf":
        from motores.tfidf import MotorTFIDF
        return MotorTFIDF()
    elif tipo == "openai":
        from motores.openai import MotorOpenAI
        return MotorOpenAI()
    elif tipo == "cohere":
        from motores.cohere import MotorCohere
        return MotorCohere()
    else:
        raise ValueError(f"Motor de interpretação desconhecido: {tipo}")
