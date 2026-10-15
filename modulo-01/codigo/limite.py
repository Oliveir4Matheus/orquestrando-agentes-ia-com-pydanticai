from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.usage import UsageLimits

from agente import agente


def modelo_teimoso(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "9999"})])


try:
    agente.run_sync(
        "Onde está o pedido 9999?",
        model=FunctionModel(modelo_teimoso),
        usage_limits=UsageLimits(request_limit=3),
    )
except UsageLimitExceeded as erro:
    print("Execução interrompida:", str(erro).split(".")[0])
