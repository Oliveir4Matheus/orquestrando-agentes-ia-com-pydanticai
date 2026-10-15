from pydantic_ai import Agent

from config import MODELO
from loja import PEDIDOS_POR_CLIENTE


def listar_pedidos(cliente: str) -> str:
    """Lista os pedidos de um cliente (código, status e data). Para ver os itens, use detalhar_pedido."""
    pedidos = PEDIDOS_POR_CLIENTE.get(cliente, {})
    return "\n".join(f"{codigo} | {p['status']} | {p['data']}" for codigo, p in pedidos.items())


def detalhar_pedido(cliente: str, codigo: str) -> str:
    """Devolve todos os dados de um único pedido do cliente."""
    pedido = PEDIDOS_POR_CLIENTE.get(cliente, {}).get(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


def despejar_tudo(cliente: str) -> str:
    return "\n".join(f"{codigo}: {p}" for codigo, p in PEDIDOS_POR_CLIENTE[cliente].items())


agente = Agent(
    MODELO,
    tools=[listar_pedidos, detalhar_pedido],
    instructions=(
        "Você atende clientes da loja Casa Verde. Liste os pedidos do cliente e "
        "detalhe apenas o necessário para responder. Responda em até duas frases."
    ),
)

if __name__ == "__main__":
    print("Tudo no contexto :", len(despejar_tudo("lia")), "caracteres")
    print("Só a lista       :", len(listar_pedidos("lia")), "caracteres")
    print("Um pedido        :", len(detalhar_pedido("lia", "2006")), "caracteres")
