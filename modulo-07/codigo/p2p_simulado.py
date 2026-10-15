import asyncio
from contextlib import ExitStack

import modelos_simulados as sim
import transferencia as t


def transferir(destino, motivo):
    return sim.saida({"destino": destino, "motivo": motivo}, tipo="transferencia")


def responder(texto):
    return sim.saida({"texto": texto}, tipo="resposta")


async def principal():
    modelos = {
        "triagem": transferir("pedidos", "a conversa anterior era sobre pedidos"),
        "pedidos": transferir("politicas", "a pergunta é sobre regras, não sobre um pedido"),
        "politicas": responder("O prazo de devolução é de 7 dias após o recebimento."),
    }
    with ExitStack() as pilha:
        for nome, modelo in modelos.items():
            pilha.enter_context(t.AGENTES[nome].override(model=modelo))
        texto, trilha = await t.atender("Qual é o prazo para devolver um produto?")
    print("Roteamento inicial (errado): pedidos")
    print("Trilha:", " -> ".join(trilha))
    print("Resposta:", texto)


asyncio.run(principal())
