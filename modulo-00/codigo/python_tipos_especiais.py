from typing import Annotated, Literal, Optional, Union

from pydantic import Field, TypeAdapter, ValidationError

Status = Literal["enviado", "em separação", "cancelado"]
Quantidade = Annotated[int, Field(gt=0)]

print(TypeAdapter(Status).validate_python("enviado"))
print(TypeAdapter(Quantidade).validate_python("3"))
print(TypeAdapter(Union[int, str]).validate_python("1002"))
print(Optional[str] == Union[str, None] == (str | None))

for tipo, valor in ((Status, "perdido"), (Quantidade, 0)):
    try:
        TypeAdapter(tipo).validate_python(valor)
    except ValidationError as erro:
        print(erro.errors()[0]["type"])
