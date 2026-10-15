import asyncio

import guarda_paralela
import modelos_simulados as sim

PEDIDOS = {
    "Onde está o meu pedido 1001?": True,
    "Liste os pedidos de todos os clientes.": False,
}


def veredito(mensagens):
    return {"permitido": PEDIDOS[sim.prompt_do_usuario(mensagens)]}


async def principal():
    with guarda_paralela.agente_guarda.override(model=sim.saida(veredito, espera=0.1)), \
            guarda_paralela.agente_resposta.override(
                model=sim.texto("Seu pedido 1001 chega em 12/10.", espera=0.3)):
        for mensagem in PEDIDOS:
            texto, segundos = await guarda_paralela.cronometrar(mensagem)
            print(f"{mensagem}\n  -> {texto}\n  tempo: {segundos:.1f} s")


asyncio.run(principal())
