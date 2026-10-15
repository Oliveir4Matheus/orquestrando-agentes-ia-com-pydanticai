from pydantic_ai import Agent, RunContext

from config import MODELO
from especialistas import especialista_pedidos, especialista_politicas

gerente = Agent(
    MODELO,
    name="gerente",
    instructions=(
        "Você é o gerente do atendimento da Casa Verde. Delegue cada parte da "
        "pergunta ao especialista certo e, com as respostas, escreva uma única "
        "mensagem ao cliente, em até três frases."
    ),
)


@gerente.tool
async def consultar_pedidos(ctx: RunContext[None], pergunta: str) -> str:
    """Delega ao especialista em pedidos uma pergunta sobre status ou previsão."""
    resposta = await especialista_pedidos.run(pergunta, usage=ctx.usage)
    return resposta.output


@gerente.tool
async def consultar_politicas(ctx: RunContext[None], pergunta: str) -> str:
    """Delega ao especialista em políticas uma pergunta sobre devolução, cancelamento ou frete."""
    resposta = await especialista_politicas.run(pergunta, usage=ctx.usage)
    return resposta.output
