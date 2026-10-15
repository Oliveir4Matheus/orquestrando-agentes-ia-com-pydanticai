import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agente = Agent(TestModel(custom_output_text="Pronto."))


@agente.tool_plain
def consultar_estoque(produto: str) -> int:
    """Devolve o estoque de um produto."""
    return 7


async def principal():
    async with agente.iter("Quanto há de estoque de vaso?") as execucao:
        async for no in execucao:
            print(type(no).__name__, "-> mensagens até aqui:", len(execucao.all_messages()))
    print("saída:", execucao.result.output)


asyncio.run(principal())
