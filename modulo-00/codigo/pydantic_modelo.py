from pydantic import BaseModel, Field, ValidationError


class Produto(BaseModel):
    nome: str = Field(min_length=3, description="Nome do produto na vitrine")
    preco: float = Field(gt=0, description="Preço em reais")
    estoque: int = Field(default=0, ge=0)
    nota: int = Field(default=5, ge=1, le=5)


vaso = Produto(nome="Vaso de barro", preco="49.90")
print(vaso)
print(vaso.preco + 10)

try:
    Produto(nome="Va", preco=-1, nota=9)
except ValidationError as erro:
    print(erro.error_count(), "erros")
    for item in erro.errors():
        print(item["loc"], item["type"], "-", item["msg"])
