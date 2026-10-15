PEDIDOS = {
    "1001": {"status": "enviado", "previsao": "12/10", "valor": 189.90},
    "1002": {"status": "em separação", "previsao": "15/10", "valor": 64.50},
    "1003": {"status": "entregue", "previsao": "01/10", "valor": 320.00},
}


def buscar_pedido(codigo: str) -> dict | None:
    return PEDIDOS.get(codigo)
