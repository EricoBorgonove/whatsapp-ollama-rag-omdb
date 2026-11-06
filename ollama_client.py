
import os
import requests

from dotenv import load_dotenv


# ==========================================
# CONFIGURACOES
# ==========================================

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

MODELO = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
Você é um assistente virtual integrado ao WhatsApp.

Instruções:
1. Responda sempre em português brasileiro.
2. Seja claro, educado e objetivo.
3. Evite respostas excessivamente longas.
4. Utilize o histórico da conversa quando necessário.
5. Não invente informações.
6. Quando não souber responder, informe a limitação.
7. Produza respostas adequadas para leitura no WhatsApp.
"""


# ==========================================
# CONSULTAR O OLLAMA
# ==========================================

def consultar_ollama(pergunta, historico=None):

    mensagens = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if historico:
        mensagens.extend(historico)

    mensagens.append({
        "role": "user",
        "content": pergunta
    })

    payload = {
        "model": MODELO,
        "messages": mensagens,
        "stream": False
    }

    resposta = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=180
    )

    resposta.raise_for_status()

    dados = resposta.json()

    texto = dados["message"]["content"].strip()

    if not texto:
        raise RuntimeError(
            "O Ollama retornou uma resposta vazia."
        )

    return texto
