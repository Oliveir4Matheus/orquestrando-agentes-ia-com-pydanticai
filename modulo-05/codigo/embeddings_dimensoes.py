from pydantic_ai import Embedder
from pydantic_ai.embeddings import TestEmbeddingModel

embedder = Embedder(TestEmbeddingModel(dimensions=4))
resultado = embedder.embed_documents_sync(["Política de devolução", "Frete grátis"])

print("Tipo do resultado:", type(resultado).__name__)
print("Textos enviados  :", resultado.inputs)
print("Vetores          :", resultado.embeddings)
