from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import react_manual
from escolhedor_simulado import modelo_escolhedor
from loja import escolhedor


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    texto = mensagens[-1].parts[0].content
    observacoes = texto.count("Observação:")
    if observacoes == 0:
        passo = (
            "Pensamento: preciso saber há quantos dias o pedido foi entregue.\n"
            "Ação: pedido[1003]"
        )
    elif observacoes == 1:
        passo = (
            "Pensamento: agora preciso do prazo de devolução da loja.\n"
            "Ação: politica[devolucao]"
        )
    else:
        passo = (
            "Pensamento: foram 3 dias e o prazo é de 7, então ainda está no prazo.\n"
            "Resposta final: Sim, você ainda pode devolver: o prazo é de 7 dias e "
            "o pedido foi entregue há 3."
        )
    return ModelResponse(parts=[TextPart(passo)])


with (
    react_manual.raciocinador.override(model=FunctionModel(modelo_roteirizado)),
    escolhedor.override(model=modelo_escolhedor),
):
    resposta = react_manual.reagir("Meu pedido 1003 chegou com defeito. Ainda consigo devolver?")
print("\nCliente recebe:", resposta)
