from pydantic import BaseModel, ValidationError, field_validator, model_validator


class Cupom(BaseModel):
    codigo: str
    desconto: float
    minimo: float = 0

    @field_validator("codigo")
    @classmethod
    def padronizar(cls, valor: str) -> str:
        valor = valor.strip().upper()
        if not valor.startswith("VERDE"):
            raise ValueError("o código deve começar com VERDE")
        return valor

    @model_validator(mode="after")
    def desconto_cabe(self) -> "Cupom":
        if self.minimo and self.desconto >= self.minimo:
            raise ValueError("o desconto precisa ser menor que a compra mínima")
        return self


print(Cupom(codigo="  verde10 ", desconto=10, minimo=100))

for dados in [{"codigo": "PROMO", "desconto": 5}, {"codigo": "verde50", "desconto": 50, "minimo": 30}]:
    try:
        Cupom.model_validate(dados)
    except ValidationError as erro:
        item = erro.errors()[0]
        print(item["loc"], "-", item["msg"])
