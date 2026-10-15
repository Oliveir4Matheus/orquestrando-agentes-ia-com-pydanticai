from pydantic import BaseModel, Field, ValidationError


class Parecer(BaseModel):
    texto: str
    confianca: float = Field(ge=0, le=1)


ok = Parecer(texto="O pedido 1003 foi entregue.", confianca=0.95)
print("Válido:", ok)

try:
    Parecer(texto="Limpe com pano úmido.", confianca=1.4)
except ValidationError as erro:
    detalhe = erro.errors()[0]
    print("Campo:", detalhe["loc"][0])
    print("Motivo:", detalhe["msg"])
