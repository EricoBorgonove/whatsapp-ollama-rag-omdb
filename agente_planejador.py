
import os
import json
import requests

from dotenv import load_dotenv

load_dotenv(".env.extensao", override=True)

URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

MODELO = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)


# ==========================================
# CATEGORIAS E FERRAMENTAS
# ==========================================

CATEGORIAS = [
    "geral",
    "rag",
    "filmes",
    "mista"
]

FERRAMENTAS = [
    "direto",
    "rag_lista",
    "rag_busca",
    "omdb_titulo",
    "omdb_busca",
    "contexto_anterior"
]


# ==========================================
# ESQUEMA JSON
# ==========================================

ESQUEMA = {
    "type": "object",
    "properties": {
        "categoria": {
            "type": "string",
            "enum": CATEGORIAS
        },
        "acoes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ferramenta": {
                        "type": "string",
                        "enum": FERRAMENTAS
                    },
                    "consulta": {
                        "type": "string"
                    },
                    "limite": {
                        "type": "integer"
                    },
                    "ano": {
                        "type": "string"
                    },
                    "detalhar": {
                        "type": "boolean"
                    }
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
    "required": [
        "categoria",
        "acoes"
    ]
}


# ==========================================
# SYSTEM PROMPT - AGENTE 1
# ==========================================

SYSTEM_PROMPT = """
Voce e o AGENTE 1, especializado em
classificar perguntas e planejar consultas.

Sua tarefa e determinar qual fonte deve
responder a pergunta do usuario.

EXISTEM QUATRO CATEGORIAS:

1. geral
Perguntas gerais sobre qualquer assunto.
Exemplos:
- O que e Python?
- Explique polimorfismo.
- O que e inteligencia artificial?
- Como funciona uma rede de computadores?
- Quanto e 10 vezes 20?
- Escreva um codigo Python.
- Explique a taxonomia de Bloom.
- O que e RAG?

Ferramenta: direto.

IMPORTANTE:
Uma pergunta geral sobre RAG nao significa
que o usuario quer consultar documentos.
RAG tambem pode ser apenas um assunto.

2. rag
Quando o usuario deseja pesquisar
os documentos indexados.

Exemplos:
- Quais artigos estao indexados?
- Liste os PDFs cadastrados.
- Segundo meus documentos, o que e RAG?
- O que os artigos dizem sobre IA?
- Compare os documentos sobre aprendizado.

Ferramentas:
rag_lista ou rag_busca.

3. filmes
Quando o usuario pergunta sobre filmes
ou series e precisa de informacoes da OMDb.

Exemplos:
- Quem dirigiu Interestelar?
- Qual a duracao de Matrix?
- Compare Batman e Superman.
- Pesquise cinco filmes com Batman no titulo.
- Qual a avaliacao IMDb de Oppenheimer?

Ferramentas:
omdb_titulo ou omdb_busca.

4. mista
Quando a pergunta precisa combinar
diferentes fontes.

Exemplos:
- Compare o conceito de IA nos meus PDFs
  com o filme Ex Machina.
- Relacione os documentos sobre robos
  com o filme Eu, Robo.

Permite combinar RAG e OMDb.

FERRAMENTAS:

direto:
Conhecimento geral do modelo Ollama.

rag_lista:
Lista os documentos indexados.

rag_busca:
Busca trechos relevantes nos PDFs.

omdb_titulo:
Consulta detalhes de um filme especifico.

omdb_busca:
Pesquisa varios titulos na OMDb.

contexto_anterior:
Reutiliza resultados da consulta anterior
quando a pergunta depende dessa consulta.

REGRAS OBRIGATORIAS:

1. Classifique primeiro a categoria.

2. Para categoria geral, use somente direto.

3. Nao consulte OMDb para perguntas de
   programacao, ciencias, matematica,
   historia ou assuntos gerais.

4. Nao consulte o RAG apenas porque
   a pergunta menciona inteligencia
   artificial ou aprendizado de maquina.

5. Use RAG quando o usuario se referir
   aos seus PDFs, documentos, artigos
   ou base de conhecimento.

6. Use OMDb para consultas factuais
   sobre filmes e series especificos.

7. Para comparar varios filmes, crie
   uma acao para cada titulo.

8. Para pesquisar varios titulos,
   utilize omdb_busca.

9. Se souber o titulo original de um
   filme com seguranca, utilize-o.

10. Se souber o ano com seguranca,
    informe o ano.

11. Nunca invente titulos ou anos.

12. Pode combinar fontes quando necessario.

13. Use no maximo quatro acoes.

14. O limite deve ficar entre 1 e 5.

15. Considere o historico da conversa.

16. Responda somente com JSON valido.

EXEMPLO - PERGUNTA GERAL:

{
  "categoria": "geral",
  "acoes": [
    {
      "ferramenta": "direto",
      "consulta": "O que e Python?",
      "limite": 1,
      "ano": "",
      "detalhar": false
    }
  ]
}

EXEMPLO - DOCUMENTOS:

{
  "categoria": "rag",
  "acoes": [
    {
      "ferramenta": "rag_lista",
      "consulta": "",
      "limite": 5,
      "ano": "",
      "detalhar": false
    }
  ]
}

EXEMPLO - FILME:

{
  "categoria": "filmes",
  "acoes": [
    {
      "ferramenta": "omdb_titulo",
      "consulta": "Interstellar",
      "limite": 1,
      "ano": "2014",
      "detalhar": true
    }
  ]
}
"""


# ==========================================
# ACAO PADRAO PARA PERGUNTAS GERAIS
# ==========================================

def acao_direta(pergunta):

    return {
        "ferramenta": "direto",
        "consulta": pergunta,
        "limite": 1,
        "ano": "",
        "detalhar": False
    }


# ==========================================
# PLANEJAR PERGUNTA
# ==========================================

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
            "options": {
                "temperature": 0
            }
        },
        timeout=180
    )

    resposta.raise_for_status()

    conteudo = resposta.json()[
        "message"
    ]["content"]

    plano = json.loads(conteudo)

    categoria = plano.get(
        "categoria", "geral"
    )

    if categoria not in CATEGORIAS:
        categoria = "geral"

    # --------------------------------------
    # PERGUNTAS GERAIS
    # --------------------------------------

    if categoria == "geral":

        return {
            "categoria": "geral",
            "acoes": [
                acao_direta(pergunta)
            ]
        }

    # --------------------------------------
    # VALIDAR ACOES
    # --------------------------------------

    acoes = []

    for acao in plano.get("acoes", [])[:4]:

        if not isinstance(acao, dict):
            continue

        ferramenta = acao.get("ferramenta")

        if ferramenta not in FERRAMENTAS:
            continue

        try:
            limite = int(acao.get("limite", 3))
        except (TypeError, ValueError):
            limite = 3

        # Evitar ferramentas de outra categoria
        if categoria == "rag" and ferramenta not in (
            "rag_lista", "rag_busca",
            "contexto_anterior"
        ):
            continue

        if categoria == "filmes" and ferramenta not in (
            "omdb_titulo", "omdb_busca",
            "contexto_anterior"
        ):
            continue

        acoes.append({
            "ferramenta": ferramenta,
            "consulta": str(
                acao.get("consulta") or ""
            ).strip()[:250],
            "limite": max(1, min(5, limite)),
            "ano": str(
                acao.get("ano") or ""
            ).strip(),
            "detalhar": (
                acao.get("detalhar") is True
            )
        })

    # --------------------------------------
    # PLANO SEM ACOES VALIDAS
    # --------------------------------------

    if not acoes:

        if categoria == "rag":
            acoes = [{
                "ferramenta": "rag_busca",
                "consulta": pergunta,
                "limite": 3,
                "ano": "",
                "detalhar": False
            }]

        elif categoria == "filmes":
            # Nao inventar um titulo se o plano
            # nao identificou uma obra.
            return {
                "categoria": "filmes",
                "acoes": [],
                "erro": (
                    "Nao foi possivel identificar "
                    "um titulo para consulta."
                )
            }

        else:
            acoes = [acao_direta(pergunta)]

    return {
        "categoria": categoria,
        "acoes": acoes
    }
