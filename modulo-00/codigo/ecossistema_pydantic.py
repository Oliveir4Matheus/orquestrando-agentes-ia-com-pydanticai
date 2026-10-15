from pydantic import BaseModel, ValidationError


class Pedido(BaseModel):
    codigo: str
    valor: float


pedido = Pedido(codigo="1002", valor="189.90")
print(pedido)
print(type(pedido.valor))

try:
    Pedido(codigo="1003", valor="caro")
except ValidationError as erro:
    print(erro.error_count(), "erro:", erro.errors()[0]["loc"], erro.errors()[0]["type"])
