from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import cot


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    nome = info.output_tools[0].name
    return ModelResponse(parts=[ToolCallPart(nome, {
        "passos": [
            "3 canecas x R$ 64,50 = R$ 193,50",
            "Desconto de 10%: 193,50 x 0,90 = R$ 174,15",
            "Valor pago por caneca: 174,15 / 3 = R$ 58,05",
            "Reembolso de 2 canecas: 58,05 x 2 = R$ 116,10",
        ],
        "valor": 116.10,
    })])


with cot.raciocinado.override(model=FunctionModel(modelo_roteirizado)):
    resposta = cot.raciocinado.run_sync(cot.PERGUNTA).output
for passo in resposta.passos:
    print("-", passo)
print("Valor:", resposta.valor)
