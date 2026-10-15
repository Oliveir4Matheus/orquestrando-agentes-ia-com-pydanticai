import json

from pydantic import BaseModel, Field


class Produto(BaseModel):
    """Um produto da loja Casa Verde."""

    nome: str = Field(min_length=3, description="Nome do produto na vitrine")
    preco: float = Field(gt=0, description="Preço em reais")
    estoque: int = Field(default=0, ge=0)


print(json.dumps(Produto.model_json_schema(), indent=2, ensure_ascii=False))
