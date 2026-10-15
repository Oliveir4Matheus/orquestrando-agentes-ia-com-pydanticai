from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import RetryPromptPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from bancada import avaliar
from contrato import agente_claro

PRIMEIRAS = {
    "Onde está o pedido 1001?": ("consultar_pedido", {"codigo": "1001"}),
    "Cadê o #1002?": ("consultar_pedido", {"codigo": "#1002"}),
    "Qual o prazo de devolução?": ("consultar_politica", {"tema": "devolucao"}),
    "O frete é grátis?": ("consultar_politica", {"tema": "frete"}),
}


def modelo_com_defeito(mensagens, info: AgentInfo) -> ModelResponse:
    partes = [parte for m in mensagens for parte in m.parts]
    if any(isinstance(p, ToolReturnPart) for p in partes):
        return ModelResponse(parts=[TextPart("ok")])
    if any(isinstance(p, RetryPromptPart) for p in partes):
        return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1002"})])
    pergunta = mensagens[0].parts[-1].content
    nome, argumentos = PRIMEIRAS[pergunta]
    return ModelResponse(parts=[ToolCallPart(nome, argumentos)])


avaliar(agente_claro, model=FunctionModel(modelo_com_defeito))
