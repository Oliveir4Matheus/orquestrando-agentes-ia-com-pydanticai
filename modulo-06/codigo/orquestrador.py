import asyncio

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO, MODELO_RAPIDO
from loja import buscar_pedido


class Subtarefa(BaseModel):
    codigo: str
    pergunta: str


class Plano(BaseModel):
    subtarefas: list[Subtarefa]


def consultar_pedido(codigo: str) -> str:
    """Consulta o status e a previsão de um pedido pelo código de 4 dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


orquestrador = Agent(
    MODELO,
    output_type=Plano,
    instructions=(
        "Divida o pedido do cliente em subtarefas independentes, uma para cada "
        "pedido citado, cada uma com uma pergunta clara."
    ),
)

trabalhador = Agent(
    MODELO_RAPIDO,
    tools=[consultar_pedido],
    instructions="Responda à subtarefa em uma frase, consultando o pedido.",
)

sintetizador = Agent(
    MODELO,
    instructions="Junte os resultados em uma única mensagem cordial, sem repetir dados.",
)


async def resolver(pedido_do_cliente: str) -> str:
    plano = (await orquestrador.run(pedido_do_cliente)).output
    respostas = await asyncio.gather(*(trabalhador.run(s.pergunta) for s in plano.subtarefas))
    resultados = "\n".join(f"- {r.output}" for r in respostas)
    final = await sintetizador.run(f"Pedido original: {pedido_do_cliente}\nResultados:\n{resultados}")
    return final.output
