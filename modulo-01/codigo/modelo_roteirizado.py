from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    retornos = [
        parte
        for mensagem in mensagens
        for parte in mensagem.parts
        if isinstance(parte, ToolReturnPart)
    ]
    if len(retornos) == 0:
        return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1001"})])
    if len(retornos) == 1:
        return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1002"})])
    return ModelResponse(parts=[TextPart("O 1001 já foi enviado; o 1002 ainda está em separação.")])
