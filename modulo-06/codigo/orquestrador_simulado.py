import asyncio
import re

import modelos_simulados as sim
import orquestrador


def planejar(mensagens):
    codigos = re.findall(r"\d{4}", sim.prompt_do_usuario(mensagens))
    return {"subtarefas": [
        {"codigo": c, "pergunta": f"Qual é o status do pedido {c}?"} for c in codigos
    ]}


def trabalhar(mensagens):
    codigo = re.search(r"\d{4}", sim.prompt_do_usuario(mensagens)).group()
    return f"Pedido {codigo}: status consultado."


def sintetizar(mensagens):
    linhas = sim.prompt_do_usuario(mensagens).count("\n- ")
    return f"Resumo com {linhas} resultados."


async def principal():
    with orquestrador.orquestrador.override(model=sim.saida(planejar, "orquestrador")), \
            orquestrador.trabalhador.override(model=sim.texto(trabalhar, "trabalhador")), \
            orquestrador.sintetizador.override(model=sim.texto(sintetizar, "sintetizador")):
        for pedido in [
            "Quero saber dos pedidos 1001 e 1002.",
            "Preciso do status dos pedidos 1001, 1002 e 1003.",
        ]:
            sim.CHAMADAS.clear()
            resposta = await orquestrador.resolver(pedido)
            print(pedido)
            print("  ->", resposta)
            print("  chamadas:", sim.CHAMADAS)


asyncio.run(principal())
