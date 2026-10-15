from dataclasses import dataclass

from pydantic import BaseModel, ValidationError


class Avaliacao(BaseModel):
    problemas: list[str]
    aprovado: bool


@dataclass
class Resultado:
    texto: str
    aprovado: bool
    rodadas: int


print(Avaliacao.model_validate({"problemas": [], "aprovado": "true"}))

try:
    Avaliacao.model_validate({"problemas": "sem empatia", "aprovado": "talvez"})
except ValidationError as erro:
    for e in erro.errors():
        print(e["loc"], "->", e["msg"])

print(Resultado("ok", "talvez", "duas"))
