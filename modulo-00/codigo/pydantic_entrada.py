from pydantic import BaseModel, Field, ValidationError


class Produto(BaseModel):
    nome: str = Field(min_length=3)
    preco: float = Field(gt=0)
    estoque: int = 0


do_banco = {"nome": "Regador", "preco": 35.0, "estoque": 12}
regador = Produto.model_validate(do_banco)
print(regador)

do_modelo = '{"nome": "Adubo 1 kg", "preco": "22.5"}'
adubo = Produto.model_validate_json(do_modelo)
print(adubo)

for texto in ['{"nome": "Terra", "preco": 0}', '{"nome": "Terra", "preco": 9,}']:
    try:
        Produto.model_validate_json(texto)
    except ValidationError as erro:
        print(erro.errors()[0]["type"], "->", texto)
