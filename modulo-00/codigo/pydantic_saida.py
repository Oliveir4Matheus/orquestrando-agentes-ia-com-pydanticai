from pydantic import BaseModel, Field


class Produto(BaseModel):
    nome: str = Field(min_length=3)
    preco: float = Field(gt=0)
    estoque: int = 0


vaso = Produto(nome="Vaso de barro", preco=49.9, estoque=4)

print(vaso.model_dump())
print(vaso.model_dump(include={"nome", "preco"}))
print(vaso.model_dump_json())

promocao = vaso.model_copy(update={"preco": 39.9})
print(promocao)
print(vaso.preco)

quebrado = vaso.model_copy(update={"preco": -5})
print(quebrado.preco)
