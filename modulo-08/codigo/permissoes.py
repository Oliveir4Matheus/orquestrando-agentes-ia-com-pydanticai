from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from config import MODELO
from loja import buscar_pedido


@dataclass
class Sessao:
    cliente: str
    permissoes: set[str] = field(default_factory=set)
    auditoria: list[str] = field(default_factory=list)


def consultar_pedido(ctx: RunContext[Sessao], codigo: str) -> str:
    """Consulta o status de um pedido."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


def reembolsar(ctx: RunContext[Sessao], codigo: str, valor: float) -> str:
    """Reembolsa um valor em um pedido. Exige a permissão `reembolsar`."""
    if "reembolsar" not in ctx.deps.permissoes:
        ctx.deps.auditoria.append(f"NEGADO reembolsar {codigo} R$ {valor:.2f}: sem permissão")
        return "Ação negada: esta sessão não tem permissão para reembolsar."
    ctx.deps.auditoria.append(f"EXECUTADO reembolsar {codigo} R$ {valor:.2f}")
    return f"Reembolso de R$ {valor:.2f} registrado para o pedido {codigo}."


agente_de_leitura = Agent(MODELO, deps_type=Sessao, tools=[consultar_pedido], name="leitura")
agente_completo = Agent(MODELO, deps_type=Sessao, tools=[consultar_pedido, reembolsar], name="completo")
