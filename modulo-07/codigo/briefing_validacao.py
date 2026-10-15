from pydantic import BaseModel, ValidationError


class Briefing(BaseModel):
    objetivo: str
    fonte: str
    formato_da_saida: str
    limite: str


try:
    Briefing(objetivo="Investigar atrasos", fonte="estoque")
except ValidationError as erro:
    for problema in erro.errors():
        print(problema["loc"], "->", problema["msg"])

vazio = Briefing(objetivo="", fonte="", formato_da_saida="", limite="")
print("Briefing com textos vazios aceito:", vazio)
