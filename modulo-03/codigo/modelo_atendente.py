import re

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo


def modelo_atendente(mensagens, info: AgentInfo) -> ModelResponse:
    """Modelo simulado: consulta o pedido citado e responde com o status."""
    ultima = mensagens[-1].parts[-1]
    if isinstance(ultima, ToolReturnPart):
        return ModelResponse(parts=[TextPart(f"Segue o status: {ultima.content.splitlines()[0]}")])
    codigo = re.search(r"\d{4}", ultima.content).group()
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": codigo})])
