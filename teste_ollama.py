
from ollama_client import consultar_ollama


# ==========================================
# MEMORIA DA CONVERSA
# ==========================================

historico = []


print("====================================")
print("      CHAT LOCAL COM OLLAMA")
print("====================================")
print("Digite sair para encerrar.\n")


while True:

    pergunta = input("Voce: ").strip()

    if pergunta.lower() == "sair":
        break

    if not pergunta:
        continue

    try:

        resposta = consultar_ollama(
            pergunta,
            historico
        )

        print("\nIA:", resposta, "\n")

        historico.append({
            "role": "user",
            "content": pergunta
        })

        historico.append({
            "role": "assistant",
            "content": resposta
        })

        # Manter as ultimas dez interacoes
        historico = historico[-20:]

    except Exception as erro:

        print("Erro:", repr(erro))
