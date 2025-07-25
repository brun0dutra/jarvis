from config.setting import CONFIG

def carregar_interface():
    metodo = CONFIG.get("interface", "terminal")

    if metodo == "terminal":
        from interfaces.terminal import InterfaceTerminal
        return InterfaceTerminal()
    elif metodo == "telegram":
        from interfaces.telegram import InterfaceTelegram
        return InterfaceTelegram()
    else:
        raise ValueError(f"Interface desconhecida: {metodo}")

