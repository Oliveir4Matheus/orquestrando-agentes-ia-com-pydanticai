from pydantic import BaseModel, ValidationError


class Afirmacao(BaseModel):
    texto: str
    trecho_id: str | None


class AfirmacaoComPadrao(BaseModel):
    texto: str
    trecho_id: str | None = None


print(Afirmacao(texto="Prazo de 7 dias", trecho_id=None))

try:
    Afirmacao(texto="Prazo de 7 dias")
except ValidationError as erro:
    print(erro.errors()[0]["type"], erro.errors()[0]["loc"])

print(AfirmacaoComPadrao(texto="Prazo de 7 dias"))
