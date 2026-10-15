import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agente = Agent(TestModel(custom_output_text="Pedido 1002 em separação."))


async def principal() -> None:
    resultado = await agente.run("Qual o status do pedido 1002?")
    print(resultado.output)

    async with agente.run_stream("E agora?") as resposta:
        async for texto in resposta.stream_text():
            print("parcial:", texto)


asyncio.run(principal())
