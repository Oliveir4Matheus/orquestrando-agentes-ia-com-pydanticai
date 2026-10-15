from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from config import MODELO
from loja import PEDIDOS_POR_CLIENTE


@dataclass
class Sessao:
    cliente: str


agente_inseguro = Agent(MODELO)


@agente_inseguro.tool_plain
def listar_pedidos_de(cliente: str) -> str:
    """Lista os três primeiros pedidos de um cliente."""
    pedidos = list(PEDIDOS_POR_CLIENTE.get(cliente, {}).items())[:3]
    return "\n".join(f"{c} | {p['status']}" for c, p in pedidos)


agente_seguro = Agent(MODELO, deps_type=Sessao)


@agente_seguro.tool
def listar_meus_pedidos(ctx: RunContext[Sessao]) -> str:
    """Lista os três primeiros pedidos do cliente que está sendo atendido."""
    pedidos = list(PEDIDOS_POR_CLIENTE.get(ctx.deps.cliente, {}).items())[:3]
    return "\n".join(f"{c} | {p['status']}" for c, p in pedidos)
