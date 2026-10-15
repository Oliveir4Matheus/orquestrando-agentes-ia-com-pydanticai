import asyncio
from itertools import cycle

import laco_adaptativo as la
import modelos_simulados as sim

novas = cycle(["reembolso do dinheiro", "devolver produto e receber reembolso"])


async def principal():
    with la.reformulador.override(model=sim.texto(lambda mensagens: next(novas))):
        fragmento, tentativas = await la.buscar_com_laco("Como faço para estornar o dinheiro da compra?")
    for consulta, pontos in tentativas:
        print(f"{pontos:.2f}  {consulta}")
    print("Fragmento encontrado:", fragmento.id if fragmento else None)


asyncio.run(principal())
