from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


@dataclass
class Cliente:
    nome: str
    pedidos_abertos: int


def espiar(mensagens, info: AgentInfo) -> ModelResponse:
    print(info.instructions)
    print("---")
    return ModelResponse(parts=[TextPart("ok")])


atendente = Agent(
    FunctionModel(espiar),
    deps_type=Cliente,
    instructions="Você é o atendente da Casa Verde.",
)


@atendente.instructions
def quem_e_o_cliente(ctx: RunContext[Cliente]) -> str:
    return f"O cliente se chama {ctx.deps.nome}."


@atendente.instructions
def pedidos(ctx: RunContext[Cliente]) -> str:
    if ctx.deps.pedidos_abertos == 0:
        return ""
    return f"Ele tem {ctx.deps.pedidos_abertos} pedido(s) em aberto."


@atendente.instructions
def horario() -> str:
    return "A loja abre às 8h."


atendente.run_sync("Oi", deps=Cliente("Ana", 2))
atendente.run_sync("Oi", deps=Cliente("Bruno", 0))
