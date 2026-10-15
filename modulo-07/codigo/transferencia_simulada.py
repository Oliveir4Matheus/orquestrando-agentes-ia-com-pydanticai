import asyncio
from contextlib import ExitStack

import modelos_simulados as sim
import transferencia as t


def transferir(destino, motivo):
    return sim.saida({"destino": destino, "motivo": motivo}, tipo="transferencia")


def responder(texto):
    return sim.saida({"texto": texto}, tipo="resposta")


CENARIOS = {
    "Onde está o pedido 1001?": {
        "triagem": transferir("pedidos", "status de pedido"),
        "pedidos": responder("Seu pedido 1001 foi enviado e chega em 12/10."),
    },
    "Meu pedido 1001 atrasou e estou muito chateado!": {
        "triagem": transferir("pedidos", "pedido atrasado"),
        "pedidos": transferir("reclamacoes", "cliente insatisfeito"),
        "reclamacoes": responder("Sinto muito pelo atraso. Vou acompanhar o pedido 1001 e retorno com a previsão."),
    },
    "Posso devolver o pedido 1003?": {
        "triagem": transferir("pedidos", "menciona um pedido"),
        "pedidos": transferir("politicas", "pergunta sobre regra"),
        "politicas": transferir("pedidos", "precisa do status"),
    },
}


async def principal():
    for mensagem, modelos in CENARIOS.items():
        with ExitStack() as pilha:
            for nome, modelo in modelos.items():
                pilha.enter_context(t.AGENTES[nome].override(model=modelo))
            texto, trilha = await t.atender(mensagem)
        print(mensagem)
        print("  trilha:", " -> ".join(trilha))
        print("  resposta:", texto)


asyncio.run(principal())
