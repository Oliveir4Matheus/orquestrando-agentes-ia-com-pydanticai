import asyncio
from contextlib import ExitStack

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.usage import UsageLimits

import modelos_simulados as sim
import pesquisa

FONTES = {
    "transportadoras": "Taxa de atraso por transportadora, em porcentagem.",
    "estoque": "Produto com mais rupturas e a quantidade.",
    "reclamacoes": "Motivo mais citado e a quantidade.",
}


async def modelo_lider(mensagens, info):
    sim.CHAMADAS.append("lider")
    retornos = [p.content for m in mensagens for p in m.parts if isinstance(p, ToolReturnPart)]
    if not retornos:
        return ModelResponse(parts=[
            ToolCallPart("delegar", {"briefing": {
                "objetivo": f"Investigar os atrasos de setembro pela fonte {fonte}.",
                "fonte": fonte,
                "formato_da_saida": formato,
                "limite": "Uma frase, sem opinião.",
            }})
            for fonte, formato in FONTES.items()
        ])
    return ModelResponse(parts=[TextPart(
        "Relatório: a RapidoSul concentra os atrasos (32%), muito acima das demais. "
        "Houve 7 rupturas de caneca, mas o atraso é o motivo de 112 reclamações. "
        "Ação: renegociar prazos com a RapidoSul."
    )])


def modelo_subagente(mensagens):
    texto = sim.prompt_do_usuario(mensagens)
    if "RapidoSul" in texto:
        return "RapidoSul: 32% de atrasos; ViaNorte: 5%; ExpressoLeste: 8%."
    if "ruptura" in texto:
        return "Caneca esmaltada: 7 rupturas."
    return "Atraso na entrega: 112 reclamações."


async def principal():
    with ExitStack() as pilha:
        pilha.enter_context(pesquisa.lider.override(model=FunctionModel(modelo_lider)))
        pilha.enter_context(pesquisa.subagente.override(model=sim.texto(modelo_subagente, "subagente")))
        resultado = await pesquisa.lider.run(
            "Por que as entregas atrasaram em setembro?",
            usage_limits=UsageLimits(request_limit=20),
        )
    print(resultado.output)
    print()
    print("Chamadas por agente:", {n: sim.CHAMADAS.count(n) for n in ("lider", "subagente")})
    print("Total de chamadas ao modelo:", resultado.usage.requests)


asyncio.run(principal())
