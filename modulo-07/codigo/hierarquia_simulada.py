import asyncio
from contextlib import ExitStack

import modelos_simulados as sim
from equipe import Equipe, de_agente, de_equipe
from especialistas import especialista_pedidos, especialista_politicas

# Nível de baixo: uma equipe de logística, com um colaborador de pedidos.
logistica = Equipe(
    [de_agente("pedidos", "Status e previsão de pedidos.", especialista_pedidos)],
    modo="rotear",
)

# Nível de cima: o topo escolhe entre a equipe de logística e o agente de políticas.
topo = Equipe(
    [
        de_equipe("logistica", "Tudo sobre pedidos e entregas.", logistica),
        de_agente("politicas", "Regras de devolução, troca e frete.", especialista_politicas),
    ],
    modo="rotear",
)


async def principal():
    with ExitStack() as pilha:
        pilha.enter_context(topo.supervisor.override(model=sim.saida({"colaborador": "logistica"}, "topo")))
        pilha.enter_context(logistica.supervisor.override(model=sim.saida({"colaborador": "pedidos"}, "logistica")))
        pilha.enter_context(especialista_pedidos.override(model=sim.texto("Pedido 1001 enviado, chega em 12/10.", "pedidos")))
        resposta = await topo.atender("Onde está o meu pedido 1001?")
    print(resposta)
    print("Cadeia de chamadas:", " -> ".join(sim.CHAMADAS))


asyncio.run(principal())
