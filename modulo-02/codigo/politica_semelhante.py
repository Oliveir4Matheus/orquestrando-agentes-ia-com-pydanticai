import asyncio

from escolhedor_simulado import modelo_escolhedor
from loja import buscar_politica, escolhedor

PEDIDOS_DO_CLIENTE = [
    "devolucao",
    "quero mandar o produto de volta",
    "até quando posso desistir da compra?",
    "vocês vendem para atacado?",
]


async def principal() -> None:
    for pedido in PEDIDOS_DO_CLIENTE:
        print(f"{pedido} -> {await buscar_politica(pedido)}")


with escolhedor.override(model=modelo_escolhedor):
    asyncio.run(principal())
