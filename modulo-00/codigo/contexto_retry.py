from dataclasses import dataclass

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ModelResponse, RetryPromptPart, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


@dataclass
class Loja:
    estoque: dict[str, int]


def modelo(mensagens, info: AgentInfo) -> ModelResponse:
    ultima = mensagens[-1].parts[-1]
    if len(mensagens) == 1:
        return ModelResponse(parts=[ToolCallPart("reservar", {"produto": "vaso de barr"})])
    if isinstance(ultima, RetryPromptPart):
        return ModelResponse(parts=[ToolCallPart("reservar", {"produto": "vaso de barro"})])
    return ModelResponse(parts=[TextPart(ultima.content)])


atendente = Agent(FunctionModel(modelo), deps_type=Loja)


@atendente.tool
def reservar(ctx: RunContext[Loja], produto: str) -> str:
    """Reserva uma unidade de um produto do estoque."""
    print(f"passo {ctx.run_step}, tentativa {ctx.retry}: {produto!r}")
    if produto not in ctx.deps.estoque:
        raise ModelRetry(f"Produto desconhecido. Opções: {list(ctx.deps.estoque)}")
    ctx.deps.estoque[produto] -= 1
    return f"Reservado. Restam {ctx.deps.estoque[produto]}."


loja = Loja({"vaso de barro": 12, "regador": 4})
resultado = atendente.run_sync("Reserve um vaso de barro.", deps=loja)
print(resultado.output)
print(loja.estoque)
