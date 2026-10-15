from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido, buscar_rastreio


def consultar_pedido(codigo: str) -> str:
    """Consulta o status e o rastreio de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    if pedido is None:
        return "Pedido não encontrado."
    return f"{pedido}\n{buscar_rastreio(codigo)}"


def criar_agente(**opcoes) -> Agent:
    return Agent(
        MODELO,
        instructions=(
            "Você atende clientes da loja Casa Verde. Consulte o pedido antes de "
            "responder e nunca invente dados. Responda em até duas frases."
        ),
        tools=[consultar_pedido],
        **opcoes,
    )


agente = criar_agente()
