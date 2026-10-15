import asyncio

import misturador as m
import modelos_simulados as sim


def mesclar(mensagens):
    pareceres = sim.prompt_do_usuario(mensagens)
    return ("Seu pedido 1003 foi entregue e você pode devolvê-lo em até 7 dias. "
            "Lave a peça só com pano úmido.") if "cuidados" in pareceres else "?"


async def principal():
    with m.agente_pedidos.override(model=sim.saida({"texto": "O pedido 1003 foi entregue.", "confianca": 0.95})), \
            m.agente_politicas.override(model=sim.saida({"texto": "A devolução vale por 7 dias.", "confianca": 0.9})), \
            m.agente_conteudo.override(model=sim.saida({"texto": "Limpe com pano úmido.", "confianca": 0.4})), \
            m.misturador.override(model=sim.texto(mesclar)):
        print(await m.responder("Meu vaso 1003 chegou sujo. Posso devolver? Como limpo?"))


asyncio.run(principal())
