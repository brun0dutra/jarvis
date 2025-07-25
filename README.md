# 🤖 Jarvis — Seu Assistente Pessoal em Python

Jarvis é um assistente pessoal escrito em Python, com arquitetura modular, escalável e adaptável a múltiplas interfaces como terminal, Telegram e, futuramente, API web ou desktop. Ele interpreta comandos inteligentes, executa tarefas úteis e responde com voz ou texto.
---
## 🚀 Funcionalidades

- ✅ Login seguro com múltiplos métodos (terminal, banco, telegram)
- 🧠 Interpretação de comandos com NLP (TF-IDF e opcional OpenAI)
- 📦 Módulos inteligentes com extração automática de parâmetros (ex: some 2 e 3)
- 🗣️ Resposta por voz (edge-tts, pyttsx3, elevenlabs, modo silencioso)
- 💬 Interfaces pluggáveis (atualmente suporta terminal e telegram)
- 🗃️ Banco de dados SQLite com:
  - 📚 Tabela de comandos/frases treinadas
  - 📝 Logs detalhados de interações
- 🧩 Arquitetura extensível: crie novos módulos com facilidade
- ✅ Separação total de camadas: Interface, Motor, Executor, Locutor, Autenticador
## ⚙️ Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/jarvis.git
cd jarvis
```

### 2. Crie o ambiente com Poetry (recomendado)

```bash
poetry install
poetry shell
```

Ou crie um ambiente manualmente com venv e instale as dependências.

### 3. Ajuste o arquivo config/setting.py

CONFIG = {\
    "login_metodo": "terminal",\
    "motor_interpretacao": "tfidf",\
    "voz_metodo": "edge",\
    "interface": "terminal"\
}

Aqui você pode escolher outros metodos de login, motor, voz, interface. basta mudar o valor !

| Login |
|---|
| Terminal | Tudo pelo terminal |

| Motor |
|---|
| tfidf | Sem ia |

| Interface |
|---|
| Terminal | Tudo pelo seu terminal |
| Telegram | Bot do seu telegram |

| Voz |
|---|
| Edge | Voz da microsoft |
| Gtts | Voz do google |

### 4. Rode o Jarvis

```bash
python src/jarvis/main.py
```


# 🧠 Exemplo de comandos

"some 5 e 3"

Jarvis extrai os parâmetros da frase automaticamente e pergunta se algo estiver faltando!

# 📦 Banco de dados

Local: data/jarvis.db

## Tabelas

comandos: Ações e frases treinadas

logs: Histórico completo de interações


Totalmente automatizado ao iniciar o Jarvis


# 💬 Modo Telegram

Você pode interagir com Jarvis via Telegram, basta alterar no setting.py:

"interface": "telegram"

> ⚠️ Insira seu token de bot no .env

# ✨ Próximos passos

[ ] Implementar Threads ou AsyncIO para múltiplas tarefas simultâneas

[ ] Interface Web

[ ] Painel de monitoramento com logs

[ ] Integração com serviços externos (YouTube, Google, etc.)


## 🔗 Links

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/brun0dutra/)



# ⭐ Contribua!

Esse projeto ainda está em evolução. Feedbacks e sugestões são muito bem-vindos!
Sinta-se livre para abrir issues ou enviar PRs.


# 📄 Licença

MIT License © 2025 — Bruno Dutra\
[MIT](https://choosealicense.com/licenses/mit/)
