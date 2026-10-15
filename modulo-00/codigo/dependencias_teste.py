from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class BancoProducao:
    def quantidade(self, produto: str) -> int:
        raise ConnectionError("sem conexão com o banco de produção")


class BancoFalso:
    def __init__(self, estoque: dict[str, int]):
        self.estoque = estoque

    def quantidade(self, produto: str) -> int:
        return self.estoque.get(produto, 0)


@dataclass
class Loja:
    banco: BancoProducao | BancoFalso


def modelo(mensagens, info: AgentInfo) -> ModelResponse:
    ultima = mensagens[-1].parts[-1]
    if isinstance(ultima, ToolReturnPart):
        return ModelResponse(parts=[TextPart(f"Temos {ultima.content} unidades.")])
    return ModelResponse(parts=[ToolCallPart("consultar_estoque", {"produto": "regador"})])


atendente = Agent(FunctionModel(modelo), deps_type=Loja)


@atendente.tool
def consultar_estoque(ctx: RunContext[Loja], produto: str) -> int:
    """Informa quantas unidades de um produto há em estoque."""
    return ctx.deps.banco.quantidade(produto)


def atender(pergunta: str) -> str:
    return atendente.run_sync(pergunta, deps=Loja(BancoProducao())).output


try:
    atender("Tem regador?")
except ConnectionError as erro:
    print("produção:", erro)

with atendente.override(deps=Loja(BancoFalso({"regador": 4}))):
    print("teste:", atender("Tem regador?"))
