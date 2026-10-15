from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido, buscar_politica


def consultar_pedido(codigo: str) -> str:
    """Consulta o status e a previsão de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


def consultar_politica(tema: str) -> str:
    """Consulta uma política da loja. Temas: devolucao, cancelamento, frete."""
    return buscar_politica(tema) or "Tema não encontrado."


especialista_pedidos = Agent(
    MODELO,
    name="especialista_pedidos",
    tools=[consultar_pedido],
    instructions="Você responde dúvidas sobre status e previsão de pedidos da Casa Verde, em uma frase.",
)

especialista_politicas = Agent(
    MODELO,
    name="especialista_politicas",
    tools=[consultar_politica],
    instructions="Você responde dúvidas sobre políticas da Casa Verde, em uma frase, citando o prazo ou valor.",
)
