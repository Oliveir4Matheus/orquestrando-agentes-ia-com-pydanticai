from documentos import DOCUMENTOS
from indice import dividir

texto = DOCUMENTOS[0]["texto"]
print("Texto:", len(texto), "caracteres\n")
for numero, trecho in enumerate(dividir(texto, tamanho=120, sobreposicao=30), start=1):
    print(f"{numero}: {trecho!r}")
