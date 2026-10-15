import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel


class Produto(BaseModel):
    nome: str
    preco: float = 0


async def json_em_pedacos(mensagens, info: AgentInfo):
    ferramenta = info.output_tools[0].name
    yield {0: DeltaToolCall(name=ferramenta, json_args='{"nome": "Vaso', tool_call_id="c1")}
    for pedaco in [' de barro"', ', "preco": 49.9}']:
        yield {0: DeltaToolCall(json_args=pedaco)}


catalogo = Agent(FunctionModel(stream_function=json_em_pedacos), output_type=Produto)


async def main():
    async with catalogo.run_stream("Cadastre o vaso de barro") as resposta:
        async for parcial in resposta.stream_output(debounce_by=None):
            print(repr(parcial))


asyncio.run(main())
