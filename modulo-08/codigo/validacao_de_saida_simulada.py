import asyncio

import guardrails as g
import modelos_simulados as sim

RESPOSTAS = iter([
    "Pode ficar tranquila: reembolso garantido em 24 horas.",
    "Vou abrir a solicitação de devolução e você receberá os próximos passos por e-mail.",
])


async def principal():
    with g.atendente.override(model=sim.texto(lambda mensagens: next(RESPOSTAS), "atendente")):
        resposta = await g.atendente.run("Quero meu dinheiro de volta!")
    print("Resposta entregue:", resposta.output)
    print("Chamadas ao modelo:", len(sim.CHAMADAS))


asyncio.run(principal())
