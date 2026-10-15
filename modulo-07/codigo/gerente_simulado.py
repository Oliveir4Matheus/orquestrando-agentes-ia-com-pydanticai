import asyncio
from contextlib import ExitStack

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

import gerente
import modelos_simulados as sim
from especialistas import especialista_pedidos, especialista_politicas


async def modelo_gerente(mensagens, info):
    sim.CHAMADAS.append("gerente")
    retornos = [p.content for m in mensagens for p in m.parts if isinstance(p, ToolReturnPart)]
    if not retornos:
        return ModelResponse(parts=[
            ToolCallPart("consultar_pedidos", {"pergunta": "Qual é o status do pedido 1003?"}),
            ToolCallPart("consultar_politicas", {"pergunta": "Qual é o prazo de devolução?"}),
        ])
    return ModelResponse(parts=[TextPart(
        "Seu pedido 1003 foi entregue, e você ainda pode devolvê-lo: o prazo é de 7 dias após o recebimento."
    )])


async def principal():
    with ExitStack() as pilha:
        pilha.enter_context(gerente.gerente.override(model=FunctionModel(modelo_gerente)))
        pilha.enter_context(especialista_pedidos.override(model=sim.texto("O pedido 1003 foi entregue.", "pedidos")))
        pilha.enter_context(especialista_politicas.override(model=sim.texto("O prazo de devolução é de 7 dias.", "politicas")))
        resultado = await gerente.gerente.run("Meu pedido 1003 chegou com defeito. Posso devolver?")

    print(resultado.output)
    print("Chamadas, em ordem:", sim.CHAMADAS)
    print("Total de chamadas ao modelo:", resultado.usage.requests)


asyncio.run(principal())
