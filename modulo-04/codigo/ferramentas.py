from loja import PEDIDOS_POR_CLIENTE


def listar_pedidos(cliente: str) -> list[dict]:
    """Lista os pedidos de um cliente. Cada item tem `codigo`, `status` e `data`."""
    pedidos = PEDIDOS_POR_CLIENTE.get(cliente, {})
    return [{"codigo": c, "status": p["status"], "data": p["data"]} for c, p in pedidos.items()]


def detalhar_pedido(cliente: str, codigo: str) -> dict:
    """Devolve os dados de um pedido: `status`, `data` e `itens` (texto, como '3x caneca; ...')."""
    pedido = PEDIDOS_POR_CLIENTE.get(cliente, {}).get(codigo)
    return pedido if pedido else {"erro": "Pedido não encontrado."}
