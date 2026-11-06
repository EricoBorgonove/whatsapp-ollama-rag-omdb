
import os
import json
import math
import re
from pathlib import Path

import requests
from dotenv import load_dotenv
from pypdf import PdfReader


# ==========================================
# CONFIGURACOES
# ==========================================

load_dotenv(".env.extensao")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

PASTA_DOCUMENTOS = Path("documents")
PASTA_INDICE = Path("dados_rag")
ARQUIVO_INDICE = PASTA_INDICE / "indice.json"


# ==========================================
# GERAR EMBEDDINGS
# ==========================================

def gerar_embeddings(textos):

    resposta = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": textos
        },
        timeout=180
    )

    resposta.raise_for_status()

    vetores = resposta.json()["embeddings"]

    if len(vetores) != len(textos):
        raise RuntimeError(
            "Quantidade de embeddings inesperada."
        )

    return vetores


# ==========================================
# DIVIDIR O TEXTO EM TRECHOS
# ==========================================

def dividir_texto(texto, tamanho=900, sobreposicao=120):

    if tamanho <= 0 or not 0 <= sobreposicao < tamanho:
        raise ValueError("Parametros de divisao invalidos.")

    texto = re.sub(r"\s+", " ", texto).strip()

    trechos = []
    inicio = 0

    while inicio < len(texto):

        fim = min(inicio + tamanho, len(texto))

        # Evitar cortar palavras no meio
        if fim < len(texto):
            ultimo_espaco = texto.rfind(
                " ", inicio + tamanho // 2, fim
            )
            if ultimo_espaco > inicio:
                fim = ultimo_espaco

        trecho = texto[inicio:fim].strip()

        if trecho:
            trechos.append(trecho)

        if fim >= len(texto):
            break

        inicio = fim - sobreposicao

    return trechos


# ==========================================
# INDEXAR DOCUMENTOS PDF
# ==========================================

def indexar_documentos():

    PASTA_DOCUMENTOS.mkdir(exist_ok=True)
    PASTA_INDICE.mkdir(exist_ok=True)

    registros = []

    arquivos = sorted(
        PASTA_DOCUMENTOS.glob("*.pdf")
    )

    if not arquivos:
        raise RuntimeError(
            "Nenhum PDF encontrado em documentos/."
        )

    for arquivo in arquivos:

        print(f"Lendo: {arquivo.name}", flush=True)

        leitor = PdfReader(str(arquivo))

        for numero_pagina, pagina in enumerate(
            leitor.pages, start=1
        ):

            texto = pagina.extract_text() or ""

            trechos = dividir_texto(texto)

            for trecho in trechos:

                registros.append({
                    "arquivo": arquivo.name,
                    "pagina": numero_pagina,
                    "texto": trecho
                })

    if not registros:
        raise RuntimeError(
            "Nenhum texto extraido dos PDFs. "
            "Verifique se os arquivos sao digitalizados."
        )

    print(
        f"Gerando embeddings de {len(registros)} trechos..."
    )

    # Processar em pequenos lotes
    for inicio in range(0, len(registros), 12):

        lote = registros[inicio:inicio + 12]

        vetores = gerar_embeddings(
            [item["texto"] for item in lote]
        )

        for item, vetor in zip(lote, vetores):
            item["embedding"] = vetor

        print(
            f"Processados: {min(inicio + 12, len(registros))}"
            f"/{len(registros)}",
            flush=True
        )

    indice = {
        "modelo": EMBEDDING_MODEL,
        "registros": registros
    }

    ARQUIVO_INDICE.write_text(
        json.dumps(indice, ensure_ascii=False),
        encoding="utf-8"
    )

    return len(registros)


# ==========================================
# SIMILARIDADE DE COSSENO
# ==========================================

def similaridade(vetor_a, vetor_b):

    if len(vetor_a) != len(vetor_b):
        raise ValueError("Vetores incompatíveis.")

    produto = sum(
        a * b for a, b in zip(vetor_a, vetor_b)
    )

    norma_a = math.sqrt(
        sum(a * a for a in vetor_a)
    )

    norma_b = math.sqrt(
        sum(b * b for b in vetor_b)
    )

    if norma_a == 0 or norma_b == 0:
        return 0.0

    return produto / (norma_a * norma_b)


# ==========================================
# CONSULTAR A BASE RAG
# ==========================================

def buscar_documentos(pergunta, quantidade=3):

    if not ARQUIVO_INDICE.exists():
        raise RuntimeError(
            "Base RAG nao encontrada. "
            "Execute indexar_pdfs.py primeiro."
        )

    indice = json.loads(
        ARQUIVO_INDICE.read_text(encoding="utf-8")
    )

    if indice["modelo"] != EMBEDDING_MODEL:
        raise RuntimeError(
            "Modelo de embeddings diferente. "
            "Reindexe os documentos."
        )

    vetor_pergunta = gerar_embeddings([pergunta])[0]

    resultados = []

    for registro in indice["registros"]:

        pontuacao = similaridade(
            vetor_pergunta,
            registro["embedding"]
        )

        resultados.append({
            "arquivo": registro["arquivo"],
            "pagina": registro["pagina"],
            "texto": registro["texto"],
            "similaridade": pontuacao
        })

    resultados.sort(
        key=lambda item: item["similaridade"],
        reverse=True
    )

    return resultados[:quantidade]



def listar_documentos():

    if not ARQUIVO_INDICE.exists():
        return []

    indice = json.loads(
        ARQUIVO_INDICE.read_text(encoding="utf-8")
    )

    documentos = {}

    for registro in indice.get("registros", []):

        nome = registro["arquivo"]

        if nome not in documentos:
            documentos[nome] = set()

        documentos[nome].add(registro["pagina"])

    return [
        {
            "arquivo": nome,
            "paginas_indexadas": len(paginas)
        }
        for nome, paginas in sorted(documentos.items())
    ]
