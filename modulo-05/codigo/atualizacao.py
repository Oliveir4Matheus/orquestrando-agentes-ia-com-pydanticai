from copy import deepcopy

from documentos import DOCUMENTOS
from indice import Fragmento, Indice

PERGUNTA = "Em quantos dias posso devolver o produto?"


def montar(documentos):
    return Indice([Fragmento(d["id"], d["titulo"], d["texto"]) for d in documentos])


antes = montar(DOCUMENTOS).buscar(PERGUNTA, k=1)[0][1]
print("Antes :", antes.texto[:62], "...")

novos = deepcopy(DOCUMENTOS)
novos[0]["texto"] = novos[0]["texto"].replace("7 dias corridos", "14 dias corridos")

depois = montar(novos).buscar(PERGUNTA, k=1)[0][1]
print("Depois:", depois.texto[:63], "...")
