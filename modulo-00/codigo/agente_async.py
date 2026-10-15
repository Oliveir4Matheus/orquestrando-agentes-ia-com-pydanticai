import asyncio

from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


PEDACOS = ["O vaso ", "de barro ", "custa R$ 49,90."]


def de_uma_vez(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart("".join(PEDACOS))])


async def em_pedacos(mensagens, info: AgentInfo):
    for pedaco in PEDACOS:
        yield pedaco


atendente = Agent(FunctionModel(de_uma_vez, stream_function=em_pedacos))


async def main():
    resultado = await atendente.run("Quanto custa o vaso?")
    print("run:", resultado.output)

    async with atendente.run_stream("Quanto custa o vaso?") as resposta:
        async for texto in resposta.stream_text(debounce_by=None):
            print("acumulado:", repr(texto))

    async with atendente.run_stream("Quanto custa o vaso?") as resposta:
        async for pedaco in resposta.stream_text(delta=True, debounce_by=None):
            print("delta:", repr(pedaco))

    async with atendente.run_stream("Quanto custa o vaso?") as resposta:
        print("get_output:", await resposta.get_output())
        print(resposta.usage)


asyncio.run(main())
