from typing import Annotated, Literal

from pydantic import Field

from pydantic_ai import Agent

from config import MODELO
from espiar import espiar_ferramentas
from loja import buscar_pedido, buscar_politica

agente_vago = Agent(MODELO)


@agente_vago.tool_plain
def politica(tema: str) -> str:
    return buscar_politica(tema) or "Tema não encontrado."


agente_claro = Agent(MODELO)


@agente_claro.tool_plain
def consultar_politica(tema: Literal["devolucao", "cancelamento", "frete"]) -> str:
    """Consulta uma política da loja.

    Args:
        tema: Assunto da política consultada.
    """
    return buscar_politica(tema) or "Tema não encontrado."


@agente_claro.tool_plain
def consultar_pedido(
    codigo: Annotated[str, Field(description="Código do pedido, com 4 dígitos", pattern=r"^\d{4}$")],
) -> str:
    """Consulta o status e a previsão de entrega de um pedido."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


if __name__ == "__main__":
    print("== Contrato vago")
    espiar_ferramentas(agente_vago)
    print("\n== Contrato claro")
    espiar_ferramentas(agente_claro)
