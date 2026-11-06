
from rag_local import buscar_documentos

print("================================")
print("       TESTE LOCAL DO RAG")
print("================================")

pergunta = "Quais são os assuntos abordados?"

try:
    resultados = buscar_documentos(
        pergunta,
        quantidade=3
    )

    print(
        f"\nTrechos encontrados: {len(resultados)}"
    )

    for numero, item in enumerate(resultados, 1):
        print(f"\n--- TRECHO {numero} ---")
        print("Arquivo:", item["arquivo"])
        print("Página:", item["pagina"])
        print("Similaridade:", item["similaridade"])
        print("Texto:", item["texto"][:400])

except Exception as erro:
    print("\nERRO:", repr(erro))

