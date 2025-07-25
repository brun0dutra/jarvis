from core.jarvis import Jarvis
from core.env import env

def main():
    env()
    jarvis = Jarvis()
    jarvis.iniciar()  # Executa normalmente

if __name__ == "__main__":
    main()
