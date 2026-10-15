import asyncio

from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior

import modelos_simulados as sim


class Seguranca(BaseModel):
    seguro: bool
    motivo: str


classificador = Agent(sim.saida({"seguro": True}, "seguranca"), output_type=Seguranca)


async def principal():
    # O classificador simulado "esquece" o campo obrigatório `motivo` nas duas tentativas.
    try:
        await classificador.run("Onde está o meu pedido 1001?")
    except UnexpectedModelBehavior as erro:
        print("Classificador falhou:", type(erro).__name__)
    print("Chamadas ao classificador:", len(sim.CHAMADAS))


asyncio.run(principal())
