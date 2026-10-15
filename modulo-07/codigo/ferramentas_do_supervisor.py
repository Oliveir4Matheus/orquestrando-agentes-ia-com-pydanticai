import asyncio

from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

from equipe import Equipe, de_agente


def espiar(mensagens, info):
    for ferramenta in info.function_tools:
        print(f"{ferramenta.name}: {ferramenta.description}")
    return ModelResponse(parts=[TextPart("ok")])


async def principal():
    equipe = Equipe(
        [
            de_agente("pedidos", "Status e previsão de entrega de pedidos.", Agent("test")),
            de_agente("politicas", "Regras de devolução, troca, frete e pagamento.", Agent("test")),
        ],
        modelo="test",
    )
    with equipe.supervisor.override(model=FunctionModel(espiar)):
        await equipe.atender("Olá")


asyncio.run(principal())
