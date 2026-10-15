from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import RetryPromptPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from aci import agente_v1, agente_v2
from trajetoria import mostrar


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    partes = [parte for m in mensagens for parte in m.parts]
    retornos = [p for p in partes if isinstance(p, ToolReturnPart)]
    if retornos:
        if retornos[-1].content.startswith("Pedido não encontrado"):
            return ModelResponse(parts=[TextPart("Não encontrei o seu pedido.")])
        return ModelResponse(parts=[TextPart("Seu pedido 1001 já foi enviado.")])
    if any(isinstance(p, RetryPromptPart) for p in partes):
        return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1001"})])
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "#1001"})])


pergunta = "Cadê o meu pedido #1001?"

print("== Ferramenta v1: o erro não diz o que fazer")
mostrar(agente_v1.run_sync(pergunta, model=FunctionModel(modelo_roteirizado)))

print("\n== Ferramenta v2: o erro orienta a correção")
mostrar(agente_v2.run_sync(pergunta, model=FunctionModel(modelo_roteirizado)))
