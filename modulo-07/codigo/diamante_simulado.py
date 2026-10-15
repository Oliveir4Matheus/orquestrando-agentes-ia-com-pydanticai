import asyncio

import diamante
import modelos_simulados as sim


async def principal():
    with diamante.especialista.override(model=sim.texto(
            "Devolução admitida em até 7 dias corridos após o recebimento, com embalagem original.")), \
            diamante.reescritor.override(model=sim.texto(
                "Claro! Você tem até 7 dias depois de receber para devolver, com a embalagem original.")):
        bruta, final = await diamante.responder("Posso devolver?")
    print("Resposta do especialista:", bruta)
    print("Resposta ao cliente     :", final)


asyncio.run(principal())
