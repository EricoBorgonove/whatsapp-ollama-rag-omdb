
from rag_local import indexar_documentos


print("====================================")
print("       INDEXACAO DE DOCUMENTOS")
print("====================================")

try:

    quantidade = indexar_documentos()

    print("\nIndexacao concluida!")
    print("Trechos indexados:", quantidade)

except Exception as erro:

    print("\nErro:", repr(erro))
