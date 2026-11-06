
import os
import requests

from dotenv import load_dotenv


load_dotenv(".env.extensao")

OMDB_URL = "https://www.omdbapi.com/"

OMDB_API_KEY = os.getenv(
    "OMDB_API_KEY", ""
).strip()


# ==========================================
# REQUISICAO A API
# ==========================================

def requisitar_omdb(parametros):

    if (
        not OMDB_API_KEY
        or OMDB_API_KEY == "COLOQUE_SUA_CHAVE_AQUI"
    ):
        raise RuntimeError(
            "Configure OMDB_API_KEY em .env.extensao"
        )

    parametros = dict(parametros)
    parametros["apikey"] = OMDB_API_KEY
    parametros["r"] = "json"

    resposta = requests.get(
        OMDB_URL,
        params=parametros,
        timeout=25
    )

    resposta.raise_for_status()

    dados = resposta.json()

    if dados.get("Response") == "False":
        raise ValueError(
            dados.get("Error", "Consulta sem resultados.")
        )

    return dados


# ==========================================
# CONSULTAR FILME POR TITULO
# ==========================================

def consultar_filme(titulo):

    return requisitar_omdb({
        "t": titulo,
        "plot": "full"
    })


# ==========================================
# PESQUISAR TITULOS
# ==========================================

def buscar_filmes(termo):

    dados = requisitar_omdb({
        "s": termo,
        "page": 1
    })

    return dados.get("Search", [])[:5]


# ==========================================
# FORMATAR INFORMACOES
# ==========================================

def formatar_filme(dados):

    campos = {
        "Título": "Title",
        "Ano": "Year",
        "Gênero": "Genre",
        "Diretor": "Director",
        "Atores": "Actors",
        "Duração": "Runtime",
        "Avaliação IMDb": "imdbRating",
        "Bilheteria": "BoxOffice",
        "Sinopse": "Plot"
    }

    linhas = []

    for rotulo, chave in campos.items():

        valor = dados.get(chave)

        if valor and valor != "N/A":
            linhas.append(f"{rotulo}: {valor}")

    return "\n".join(linhas)
