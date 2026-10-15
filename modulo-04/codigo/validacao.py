from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import RetryPromptPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from contrato import agente_claro
from trajetoria import mostrar


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    partes = [parte for m in mensagens for parte in m.parts]
    if any(isinstance(p, ToolReturnPart) for p in partes):
        return ModelResponse(parts=[TextPart("Você tem 7 dias após o recebimento para devolver.")])
    if any(isinstance(p, RetryPromptPart) for p in partes):
        return ModelResponse(parts=[ToolCallPart("consultar_politica", {"tema": "devolucao"})])
    return ModelResponse(parts=[ToolCallPart("consultar_politica", {"tema": "garantia"})])


resultado = agente_claro.run_sync(
    "Qual é o prazo para devolver um produto?", model=FunctionModel(modelo_roteirizado)
)
mostrar(resultado)
