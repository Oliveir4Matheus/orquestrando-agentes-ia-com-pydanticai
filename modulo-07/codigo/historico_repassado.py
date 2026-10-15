import asyncio

from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

import modelos_simulados as sim
from config import MODELO
from equipe import Equipe, de_agente

colaborador = Agent(MODELO, name="colaborador")


def espiar(mensagens, info):
    return ModelResponse(parts=[TextPart(f"vi {len(mensagens)} mensagem(ns)")])


async def principal():
    for repassar in (False, True):
        equipe = Equipe([de_agente("pedidos", "Status de pedidos.", colaborador, repassar_historico=repassar)])
        conversa = [
            *(await equipe.supervisor.run("oi", model=sim.texto("Olá!"))).all_messages(),
        ]
        with equipe.supervisor.override(model=sim.chamar_ferramentas([("pedidos", {"pergunta": "E o 1002?"})])), \
                colaborador.override(model=FunctionModel(espiar)):
            resposta = await equipe.atender("E o 1002?", historico=conversa)
        print(f"repassar_historico={repassar}: colaborador {resposta}")


asyncio.run(principal())
