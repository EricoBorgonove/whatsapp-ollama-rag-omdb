
import json

from agentes_autonomos import (
    pesquisar_com_ia,
    responder_com_ia
)

historico = []

print("====================================")
print("       TESTE DOS DOIS AGENTES")
print("====================================")

while True:

    pergunta = input("\nVoce: ").strip()

    if pergunta.lower() == "sair":
        break

    if not pergunta:
        continue

    try:

        pesquisa = pesquisar_com_ia(
            pergunta,
            historico
        )

        print("\nPESQUISA EXECUTADA:")
        print(json.dumps(
            pesquisa,
            ensure_ascii=False,
            indent=2
        )[:5000])

        resposta = responder_com_ia(
            pergunta,
            pesquisa,
            historico
        )

        print("\nIA:", resposta)

        historico.extend([
            {"role": "user", "content": pergunta},
            {"role": "assistant", "content": resposta}
        ])

        historico = historico[-12:]

    except Exception as erro:
        print("\nERRO:", repr(erro))
