from pydantic_ai import Agent, ModelResponse, ToolCallPart
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.usage import UsageLimits


async def modelo_em_laco(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart("consultar", {})])


agente = Agent(FunctionModel(modelo_em_laco))


@agente.tool_plain
def consultar() -> str:
    return "sem novidades"


try:
    agente.run_sync("Onde está o pedido?", usage_limits=UsageLimits(request_limit=3))
except UsageLimitExceeded as erro:
    print(type(erro).__name__)
    print(erro)
