from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from agente import agente


def modelo_teimoso(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "9999"})])


agente.run_sync("Onde está o pedido 9999?", model=FunctionModel(modelo_teimoso))
