import re

from pydantic_ai import Agent, ModelRetry

from config import MODELO
from loja import buscar_pedido

agente_v1 = Agent(MODELO)


@agente_v1.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


agente_v2 = Agent(MODELO)


@agente_v2.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido. O código tem 4 dígitos, sem '#' nem espaços (exemplo: 1001)."""
    if not re.fullmatch(r"\d{4}", codigo):
        raise ModelRetry(f"Código inválido: '{codigo}'. Envie só os 4 dígitos, como 1001.")
    pedido = buscar_pedido(codigo)
    if pedido is None:
        return f"Nenhum pedido com o código {codigo}. Peça ao cliente para conferir o número."
    return str(pedido)
