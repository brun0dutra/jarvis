from core.autenticador import carregar_login
from core.interpretador import carregar_motor
from core.executor import carregar_modulo
from core.locutor import carregar_locutor
from core.interface import carregar_interface
from database.gerenciador import registrar_log


class Jarvis:
    def iniciar(self):
        login = carregar_login()
        if not login.autenticar():
            return

        print("✅ Login bem-sucedido!")

        motor = carregar_motor()
        falar = carregar_locutor()
        interface = carregar_interface()

        while True:
            frase = interface.receber_entrada()
            if frase.lower() in ["sair", "exit", "tchau"]:
                interface.exibir_resposta("Tchau!")
                break

            acao, parametros, faltando = motor.interpretar(frase)
            modulo = carregar_modulo(acao)

            for chave, pergunta in faltando.items():
                resposta = interface.receber_entrada(pergunta)
                parametros[chave] = resposta

            resultado = modulo.executar(**parametros)

            if isinstance(resultado, tuple):
                resposta = resultado[0]
                fala = resultado[1] if len(resultado) > 1 else resposta
            else:
                resposta = resultado
                fala = resultado

            interface.exibir_resposta(resposta)
            falar(fala)
            registrar_log(frase, acao, parametros, resposta)
