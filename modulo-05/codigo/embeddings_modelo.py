from pydantic_ai import Embedder
from pydantic_ai.embeddings import TestEmbeddingModel

from busca import FRAGMENTOS
from indice import Indice

# Em produção: Embedder("openai:text-embedding-3-small"). Aqui, um modelo de teste, sem rede.
embedder = Embedder(TestEmbeddingModel(dimensions=16))


def embedar(textos: list[str]) -> list[list[float]]:
    resultado = embedder.embed_documents_sync(textos)
    return [list(vetor) for vetor in resultado.embeddings]


indice_semantico = Indice(FRAGMENTOS, embedar=embedar)
achados = indice_semantico.buscar("Posso devolver o produto?", k=2)
print("Índice criado e consultado com o Embedder:", len(achados), "fragmentos devolvidos")
