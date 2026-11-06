
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.extensao", override=True)

URL = os.getenv(
    "OLLAMA_URL", "http://localhost:11434"
).rstrip("/")

MODELO = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

FERRAMENTAS = [
    "direto",
    "rag_lista",
    "rag_busca",
    "omdb_titulo",
    "omdb_busca",
    "contexto_anterior"
]

ESQUEMA = {
    "type": "object",
    "properties": {
        "acoes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ferramenta": {
                        "type": "string",
                        "enum": FERRAMENTAS
                    },
                    "consulta": {"type": "string"},
                    "limite": {"type": "integer"},
                    "ano": {"type": "string"},
                    "detalhar": {"type": "boolean"}
                },
                "required": [
                    "ferramenta",
                    "consulta",
                    "limite",
                    "ano",
                    "detalhar"
                ]
            }
        }
    },
    "required": ["acoes"]
}

SYSTEM_PROMPT = """
Voce e o AGENTE 1, um planejador de consultas.

Sua unica tarefa e selecionar ferramentas e
produzir um plano em JSON.

FERRAMENTAS DISPONIVEIS:

direto:
Perguntas gerais que nao exigem dados externos.

rag_lista:
Listar os documentos indexados.
Use quando perguntarem quais PDFs ou artigos
estao cadastrados.

rag_busca:
Pesquisar conteudo nos documentos PDF.
Informe termos de pesquisa relevantes.
O limite representa a quantidade de trechos.

omdb_titulo:
Consultar detalhes de um filme ou serie.
A consulta deve conter o titulo.
Informe o ano quando conhecido.

omdb_busca:
Procurar varios filmes ou series pelo titulo,
palavra-chave ou parte do titulo.
A OMDb nao oferece busca geral por diretor,
genero ou maiores bilheterias.
Nao use essas condicoes como se fossem filtros.

contexto_anterior:
Reutilizar resultados da consulta anterior,
quando o usuario pedir uma continuacao.

REGRAS:
1. Escolha a ferramenta mais adequada.
2. Utilize varias acoes quando necessario.
3. Para comparar dois filmes, consulte ambos.
4. Pode combinar RAG e OMDb.
5. Nunca invente titulos ou documentos.
6. Use no maximo quatro acoes.
7. Use limite entre 1 e 5.
8. Para omdb_busca, detalhar=true permite
   obter detalhes dos resultados encontrados.
9. Utilize rag_lista quando a pergunta solicitar
   os nomes dos arquivos indexados.
10. Considere o historico para resolver perguntas
    de continuacao.
11. Se nenhuma ferramenta for necessaria,
    escolha direto.
12. Responda exclusivamente com JSON valido.

REGRAS ADICIONAIS PARA FILMES:

13. Ao identificar um filme conhecido por um
    titulo traduzido, prefira o titulo original
    quando tiver certeza da correspondencia.

14. Quando souber o ano de lancamento com
    seguranca, informe o ano na acao.

15. Diferencie filmes de series.

16. Para perguntas sobre um filme especifico,
    utilize omdb_titulo.

17. Para buscar varios titulos que compartilham
    palavras, utilize omdb_busca.

18. Para comparar filmes, crie uma acao
    separada para cada obra.

19. Nao invente titulos originais, anos
    ou identificadores IMDb.

20. Quando houver ambiguidade, preserve
    o titulo informado pelo usuario.


Formato esperado:
{
  "acoes": [
    {
      "ferramenta": "rag_busca",
      "consulta": "aprendizado de maquina",
      "limite": 3,
      "ano": "",
      "detalhar": false
    }
  ]
}
"""


def planejar(pergunta, historico=None):

    mensagens = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if historico:
        mensagens.extend(historico[-6:])

    mensagens.append({
        "role": "user",
        "content": pergunta
    })

    resposta = requests.post(
        f"{URL}/api/chat",
        json={
            "model": MODELO,
            "messages": mensagens,
            "format": ESQUEMA,
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=180
    )

    resposta.raise_for_status()

    conteudo = resposta.json()["message"]["content"]

    plano = json.loads(conteudo)

    if not isinstance(plano.get("acoes"), list):
        raise ValueError("Plano sem lista de acoes.")

    acoes = []

    for acao in plano["acoes"][:4]:

        if not isinstance(acao, dict):
            continue

        ferramenta = acao.get("ferramenta")

        if ferramenta not in FERRAMENTAS:
            continue

        try:
            limite = int(acao.get("limite", 3))
        except (ValueError, TypeError):
            limite = 3

        acoes.append({
            "ferramenta": ferramenta,
            "consulta": str(
                acao.get("consulta") or ""
            ).strip()[:250],
            "limite": max(1, min(5, limite)),
            "ano": str(
                acao.get("ano") or ""
            ).strip(),
            "detalhar": acao.get("detalhar") is True
        })

    if not acoes:
        acoes = [{
            "ferramenta": "direto",
            "consulta": pergunta,
            "limite": 1,
            "ano": "",
            "detalhar": False
        }]

    return {"acoes": acoes}
