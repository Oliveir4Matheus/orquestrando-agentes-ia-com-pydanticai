import asyncio
from contextlib import ExitStack

import blocos
import fluxo_casa_verde as f
import modelos_simulados as sim


async def principal():
    estado = {"mensagem": "Vocês têm loja física?"}
    with ExitStack() as pilha:
        pilha.enter_context(f.classificador.override(model=sim.saida({"categoria": "outro"})))
        pilha.enter_context(f.generalista.override(model=sim.texto("Vou encaminhar você a um atendente.")))
        await f.fluxo(estado)
    print("Ordem das etapas:", blocos.REGISTRO)
    print("Resposta final:", estado["resposta"])


asyncio.run(principal())
