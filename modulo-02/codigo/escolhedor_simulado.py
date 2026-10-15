from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

PALAVRAS = {
    "devolucao": ["devol", "de volta", "arrepend"],
    "cancelamento": ["cancel", "desist"],
    "frete": ["frete", "entrega"],
}


def escolher(mensagens, info: AgentInfo) -> ModelResponse:
    pedido = mensagens[-1].parts[0].content.lower()
    for tema, palavras in PALAVRAS.items():
        for palavra in palavras:
            if palavra in pedido:
                return ModelResponse(parts=[TextPart(tema)])
    return ModelResponse(parts=[TextPart("nenhuma")])


modelo_escolhedor = FunctionModel(escolher)
