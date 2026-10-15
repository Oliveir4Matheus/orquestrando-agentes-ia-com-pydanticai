import asyncio

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

import aprovacao as a


def montar_modelo(valor):
    def modelo(mensagens, info):
        retornos = [p.content for m in mensagens for p in m.parts if isinstance(p, ToolReturnPart)]
        if not retornos:
            return ModelResponse(parts=[ToolCallPart("reembolsar", {"codigo": "1001", "valor": valor})])
        return ModelResponse(parts=[TextPart(f"Resultado para você: {retornos[-1]}")])

    return FunctionModel(modelo)


async def gerente_que_aprova(pedido):
    return True, "pedido conferido: produto danificado, dentro da política"


async def gerente_que_nega(pedido):
    return False, "prazo de devolução expirado"


async def ausente(pedido):
    await asyncio.sleep(5)
    return True, "nunca chega"


def revisor(nome, funcao):
    return {"nome": nome, "decidir": funcao}


async def cenario(titulo, valor, revisores):
    a.REGISTRO.clear()
    resposta = await a.atender("Quero o reembolso do pedido 1001.", revisores, model=montar_modelo(valor))
    print(f"\n== {titulo}\nResposta: {resposta}")
    for linha in a.REGISTRO:
        print("  registro:", {k: v for k, v in linha.items() if k != "quando"})


async def principal():
    await cenario("R$ 40: dentro da alçada, sem revisão", 40.0, [])
    await cenario("R$ 250: o gerente aprova", 250.0, [revisor("gerente", gerente_que_aprova)])
    await cenario("R$ 250: o gerente nega", 250.0, [revisor("gerente", gerente_que_nega)])
    await cenario("R$ 250: o gerente não responde; a diretora aprova", 250.0,
                  [revisor("gerente", ausente), revisor("diretora", gerente_que_aprova)])
    await cenario("R$ 250: ninguém responde", 250.0, [revisor("gerente", ausente)])


asyncio.run(principal())
