from documentos import DOCUMENTOS
from indice import Fragmento, Indice

FRAGMENTOS = [Fragmento(d["id"], d["titulo"], d["texto"]) for d in DOCUMENTOS]
indice = Indice(FRAGMENTOS)

PERGUNTAS = [
    "Posso devolver o produto depois de 10 dias?",
    "Quanto custa o frete para o interior?",
    "Como faço para estornar o dinheiro da compra?",
]

if __name__ == "__main__":
    for pergunta in PERGUNTAS:
        print(pergunta)
        for pontos, fragmento in indice.buscar(pergunta, k=2):
            print(f"  {pontos:.2f}  {fragmento.id}")
