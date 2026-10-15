from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError

Codigo = Annotated[str, Field(description="Código do pedido, com 4 dígitos", pattern=r"^\d{4}$")]

adaptador = TypeAdapter(Codigo)

print(adaptador.json_schema())
print(adaptador.validate_python("2001"))

try:
    adaptador.validate_python("20A1")
except ValidationError as erro:
    print(erro.errors()[0]["msg"])
