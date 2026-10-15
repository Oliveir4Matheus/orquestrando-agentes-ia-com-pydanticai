PEDIDOS = {
    "1001": {"status": "enviado", "previsao": "12/10", "valor": 189.90},
    "1002": {"status": "em separação", "previsao": "15/10", "valor": 64.50},
    "1003": {"status": "entregue", "previsao": "01/10", "valor": 320.00, "dias_desde_entrega": 3},
}

POLITICAS = {
    "devolucao": "Devolução em até 7 dias após o recebimento, com o produto na embalagem original.",
    "cancelamento": "Cancelamento apenas enquanto o pedido estiver em separação.",
    "frete": "Frete grátis para compras acima de R$ 200.",
}


def buscar_pedido(codigo: str) -> dict | None:
    return PEDIDOS.get(codigo)


def buscar_politica(tema: str) -> str | None:
    return POLITICAS.get(tema)


def buscar_rastreio(codigo: str) -> str:
    """Histórico detalhado de movimentações do pedido, com uma linha por evento."""
    return "\n".join(
        f"{dia:02d}/09 {hora}:00 - pedido {codigo}: movimentação registrada no centro de distribuição {dia}"
        for dia, hora in zip(range(10, 22), range(8, 20))
    )


def _gerar_pedidos_da_lia() -> dict[str, dict]:
    situacoes = ["entregue", "enviado", "em separação", "entregue"]
    pedidos = {}
    for numero in range(1, 41):
        pedidos[str(2000 + numero)] = {
            "status": situacoes[numero % 4],
            "data": f"{1 + numero % 28:02d}/09",
            "itens": (
                f"{1 + numero % 4}x caneca esmaltada; 1x vaso de cerâmica; embalagem de presente; "
                "observação do cliente: entregar no período da tarde, portaria com interfone "
                "e retirada autorizada para o vizinho do apartamento ao lado."
            ),
        }
    return pedidos


PEDIDOS_POR_CLIENTE = {"lia": _gerar_pedidos_da_lia()}
