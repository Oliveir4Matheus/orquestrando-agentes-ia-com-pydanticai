from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido, buscar_politica

agente = Agent(
    MODELO,
    instructions=(
        "Você atende clientes da loja Casa Verde. Use as ferramentas para "
        "consultar dados e regras antes de responder; nunca invente. "
        "Responda em até três frases."
    ),
)


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


@agente.tool_plain
async def consultar_politica(tema: str) -> str:
    """Consulta uma política da loja. Temas: devolucao, cancelamento, frete."""
    politica = await buscar_politica(tema)
    return politica or "Tema não encontrado."
