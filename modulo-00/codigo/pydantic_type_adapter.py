from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class Item(BaseModel):
    nome: str
    quantidade: int = Field(gt=0)


Carrinho = TypeAdapter(list[Item])

carrinho = Carrinho.validate_json('[{"nome": "Vaso", "quantidade": "2"}, {"nome": "Adubo", "quantidade": 1}]')
print(carrinho)
print(Carrinho.dump_python(carrinho))
print(Carrinho.dump_json(carrinho))

Nota = TypeAdapter(Annotated[int, Field(ge=1, le=5)])
print(Nota.validate_python("4"))
try:
    Nota.validate_python(7)
except ValidationError as erro:
    print(erro.errors()[0]["type"])

print(Nota.json_schema())
