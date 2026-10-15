import asyncio
from contextlib import ExitStack

import blocos
import fluxo_casa_verde as f
import modelos_simulados as sim


def redigir(mensagens):
    if "Corrija:" in sim.prompt_do_usuario(mensagens):
        return "Sinto muito pela demora com o pedido 1001. Ele já foi enviado e chega em 12/10."
    return "Garantimos entrega imediata e reembolso total."


def avaliar(mensagens):
    if "Garantimos" in sim.prompt_do_usuario(mensagens):
        return {"problemas": ["promete reembolso e prazo não confirmados"], "aprovado": False}
    return {"problemas": [], "aprovado": True}


async def principal():
    estado = {"mensagem": "O pedido 1001 está atrasado e ninguém responde!"}
    with ExitStack() as pilha:
        pilha.enter_context(f.classificador.override(model=sim.saida({"categoria": "reclamacao"})))
        pilha.enter_context(f.redator.override(model=sim.texto(redigir)))
        pilha.enter_context(f.avaliador.override(model=sim.saida(avaliar)))
        await f.fluxo(estado)

    print("Ordem das etapas:", blocos.REGISTRO)
    print("Pedido encontrado:", estado["pedido"])
    print("Resposta final:", estado["resposta"])


asyncio.run(principal())
