
import json

from dotenv import load_dotenv

load_dotenv(".env.extensao", override=True)

from agente_planejador import planejar
from motor_ferramentas import (
    executar_plano,
    analisar_resultados
)


historico = []
resultados_anteriores = None

print("====================================")
print("      TESTE DOS DOIS AGENTES")
print("====================================")
print("Digite sair para encerrar.\n")


while True:

    pergunta = input("\nVoce: ").strip()

    if pergunta.lower() == "sair":
        break

    if not pergunta:
        continue

    try:

        print("\n[1] Planejando...")

        plano = planejar(
            pergunta,
            historico
        )

        print(json.dumps(
            plano,
            ensure_ascii=False,
            indent=2
        ))

        print("\n[2] Executando ferramentas...")

        resultados = executar_plano(
            plano,
            pergunta,
            resultados_anteriores
        )

        print(json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2
        )[:3000])

        print("\n[3] Gerando resposta...")

        resposta = analisar_resultados(
            pergunta,
            resultados,
            historico
        )

        print("\nIA:", resposta)

        historico.extend([
            {"role": "user", "content": pergunta},
            {"role": "assistant", "content": resposta}
        ])

        historico = historico[-12:]
        resultados_anteriores = resultados

    except Exception as erro:

        print("\nERRO:", repr(erro))
