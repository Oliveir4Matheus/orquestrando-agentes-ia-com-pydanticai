from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


@dataclass
class Loja:
    nome: str
    estoque: dict[str, int]


def modelo(mensagens, info: AgentInfo) -> ModelResponse:
    ultima = mensagens[-1].parts[-1]
    if isinstance(ultima, ToolReturnPart):
        return ModelResponse(parts=[TextPart(f"Temos {ultima.content} unidades.")])
    return ModelResponse(parts=[ToolCallPart("consultar_estoque", {"produto": "vaso de barro"})])


atendente = Agent(FunctionModel(modelo), deps_type=Loja)


@atendente.tool
def consultar_estoque(ctx: RunContext[Loja], produto: str) -> int:
    """Informa quantas unidades de um produto há na loja do cliente."""
    print("  consultando a loja", ctx.deps.nome)
    return ctx.deps.estoque.get(produto, 0)


centro = Loja("Centro", {"vaso de barro": 12})
bairro = Loja("Bairro Alto", {"vaso de barro": 3})

for loja in [centro, bairro]:
    resultado = atendente.run_sync("Tem vaso de barro?", deps=loja)
    print(resultado.output)
