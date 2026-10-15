from dataclasses import dataclass

from pydantic import BaseModel, ValidationError


@dataclass
class RegistroSimples:
    id: str
    latencia_s: float


class RegistroValidado(BaseModel):
    id: str
    latencia_s: float


simples = RegistroSimples(id="a1-0", latencia_s="rápido")
print("dataclass aceitou:", simples.latencia_s)

try:
    RegistroValidado(id="a1-0", latencia_s="rápido")
except ValidationError as erro:
    print("BaseModel recusou:", erro.errors()[0]["msg"])
