from pydantic_ai import Agent

import instrumentacao  # noqa: F401
from config import MODELO
from loja import buscar_pedido, buscar_politica


def consultar_pedido(codigo: str) -> str:
    """Consulta o status e a previsão de entrega de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


def consultar_politica(tema: str) -> str:
    """Consulta uma política da loja. Temas: devolucao, cancelamento, frete."""
    return buscar_politica(tema) or "Tema não encontrado."


atendente = Agent(
    MODELO,
    name="atendente",
    tools=[consultar_pedido, consultar_politica],
    instructions=(
        "Você atende clientes da Casa Verde. Use as ferramentas para consultar pedidos "
        "e políticas; nunca invente. Perguntas fora do atendimento da loja devem ser "
        "recusadas com educação. Responda em até duas frases."
    ),
)
