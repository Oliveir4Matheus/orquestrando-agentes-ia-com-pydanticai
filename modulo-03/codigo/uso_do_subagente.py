from pydantic_ai import Agent, ModelResponse, RunContext, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

sub = Agent(TestModel(custom_output_text="Pedido 2006 em separação."))
principal = Agent(
    FunctionModel(
        lambda mensagens, info: (
            ModelResponse(parts=[TextPart("Pronto.")])
            if len(mensagens) > 1
            else ModelResponse(parts=[ToolCallPart("consultar", {"pergunta": "status?"})])
        )
    )
)


@principal.tool
async def consultar(ctx: RunContext[None], pergunta: str) -> str:
    await sub.run(pergunta, usage=ctx.usage)  # sem usage=, o consumo do subagente some do total
    return "ok"


print("Requisições contadas:", principal.run_sync("Oi").usage.requests)
