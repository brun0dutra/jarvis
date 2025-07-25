from config.setting import CONFIG

def carregar_login():
    metodo = CONFIG.get("login_metodo")

    if metodo == "terminal":
        from login.terminal import LoginTerminal
        return LoginTerminal()

#    elif metodo == "banco":
        from login.banco import LoginBanco
        return LoginBanco()

#    elif metodo == "telegram":
        from login.telegram import LoginTelegram
        return LoginTelegram()

    else:
        raise ValueError(f"Login desconhecido: {metodo}")
