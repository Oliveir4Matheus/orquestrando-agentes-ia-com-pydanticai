from pydantic_ai import Agent

from config import MODELO

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

LISTA_DE_POLITICAS = "\n".join(f"- {tema}: {texto}" for tema, texto in POLITICAS.items())

escolhedor = Agent(
    MODELO,
    instructions=(
        "Você escolhe a política da loja Casa Verde que atende à necessidade do "
        "cliente. As políticas são:\n"
        f"{LISTA_DE_POLITICAS}\n"
        "Responda apenas com o nome do tema mais adequado, sem explicação. "
        "Se nenhuma política servir, responda: nenhuma."
    ),
)


def buscar_pedido(codigo: str) -> dict | None:
    return PEDIDOS.get(codigo)


async def buscar_politica(tema: str) -> str | None:
    resultado = await escolhedor.run(tema)
    escolhido = resultado.output.strip().lower()
    return POLITICAS.get(escolhido)
