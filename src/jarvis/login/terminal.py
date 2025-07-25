from login.base import LoginBase

class LoginTerminal(LoginBase):
    def autenticar(self) -> bool:
        usuario = input("Usuário: ")
        senha = input("Senha: ")
        return usuario == "admin" and senha == "1234"
