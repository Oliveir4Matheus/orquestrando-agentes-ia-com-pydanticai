import asyncio

import equipe
import modelos_simulados as sim
from especialistas import especialista_pedidos, especialista_politicas
from equipe import Colaborador, Equipe, de_agente

PERGUNTA = "Onde está o meu pedido 1001?"


def montar(modo, supervisor):
    colaboradores = [
        de_agente("pedidos", "Status e previsão de entrega de pedidos.", especialista_pedidos),
        de_agente("politicas", "Regras de devolução, troca, frete e pagamento.", especialista_politicas),
    ]
    equipe_ = Equipe(colaboradores, modo=modo)
    return equipe_, equipe_.supervisor.override(model=supervisor)


async def executar(modo, supervisor):
    sim.CHAMADAS.clear()
    equipe_, substituicao = montar(modo, supervisor)
    with substituicao, especialista_pedidos.override(model=sim.texto("Pedido 1001 enviado, chega em 12/10.", "colaborador")):
        resposta = await equipe_.atender(PERGUNTA)
    print(f"Modo {modo}: {resposta}")
    print("  chamadas:", sim.CHAMADAS)


async def principal():
    await executar("rotear", sim.saida({"colaborador": "pedidos"}, "supervisor"))
    await executar("coordenar", sim.chamar_ferramentas([("pedidos", {"pergunta": PERGUNTA})], "supervisor"))

    colaboradores = [Colaborador(f"agente{i}", "faz algo", None) for i in range(11)]
    try:
        Equipe(colaboradores)
    except ValueError as erro:
        print("Com 11 colaboradores:", erro)


asyncio.run(principal())
