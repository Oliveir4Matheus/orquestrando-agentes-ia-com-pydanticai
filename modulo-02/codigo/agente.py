from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido

agente = Agent(
    MODELO,
    instructions=(
        "Você atende clientes da loja Casa Verde. Consulte o pedido antes de "
        "responder e nunca invente dados. Responda em até duas frases."
    ),
)


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


if __name__ == "__main__":
    resultado = agente.run_sync("Onde está o meu pedido 1001?")
    print(resultado.output)
    print("Chamadas ao modelo:", resultado.usage.requests)

    resultado = agente.run_sync("Cadê a minha cadeira? O pedido é o mil e dois.")
    print(resultado.output)
