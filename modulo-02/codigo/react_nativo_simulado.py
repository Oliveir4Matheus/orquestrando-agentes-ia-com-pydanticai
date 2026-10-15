from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from escolhedor_simulado import modelo_escolhedor
from loja import escolhedor
from react_nativo import agente
from trajetoria import mostrar


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    retornos = [
        parte
        for mensagem in mensagens
        for parte in mensagem.parts
        if isinstance(parte, ToolReturnPart)
    ]
    if len(retornos) == 0:
        return ModelResponse(parts=[
            TextPart("Vou ver há quantos dias o pedido foi entregue."),
            ToolCallPart("consultar_pedido", {"codigo": "1003"}),
        ])
    if len(retornos) == 1:
        return ModelResponse(parts=[
            TextPart("Agora preciso do prazo de devolução."),
            ToolCallPart("consultar_politica", {"tema": "devolucao"}),
        ])
    return ModelResponse(parts=[TextPart("Sim: o prazo é de 7 dias e o pedido foi entregue há 3.")])


with escolhedor.override(model=modelo_escolhedor):
    resultado = agente.run_sync(
        "Meu pedido 1003 chegou com defeito. Ainda consigo devolver?",
        model=FunctionModel(modelo_roteirizado),
    )
mostrar(resultado)
