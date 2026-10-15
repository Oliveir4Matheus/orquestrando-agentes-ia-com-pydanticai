from typing import Literal

from pydantic import BaseModel, ValidationError


class Rota(BaseModel):
    categoria: Literal["reclamacao", "outro"]


print(Rota(categoria="reclamacao"))

try:
    Rota(categoria="reclamação")
except ValidationError as erro:
    print(erro.errors()[0]["type"])
    print(erro.errors()[0]["msg"])
