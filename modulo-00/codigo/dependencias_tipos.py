from dataclasses import dataclass

from pydantic import BaseModel

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel


@dataclass
class Loja:
    nome: str


class Resposta(BaseModel):
    texto: str


atendente: Agent[Loja, Resposta] = Agent(TestModel(), deps_type=Loja, output_type=Resposta)


@atendente.instructions
def nome_da_loja(ctx: RunContext[Loja]) -> str:
    return f"Você atende a loja {ctx.deps.nome}."


print(atendente.deps_type.__name__, atendente.output_type.__name__)
resultado = atendente.run_sync("Oi", deps=Loja("Centro"))
print(repr(resultado.output))

try:
    atendente.run_sync("Oi", deps="Centro")
except AttributeError as erro:
    print("deps errada:", erro)
