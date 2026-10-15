from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import compactacao
from sessao import conversar


def modelo_resumidor(mensagens, info: AgentInfo) -> ModelResponse:
    texto = (
        "Pedido 1001 enviado, previsão 12/10. Pedido 1002 em separação, previsão 15/10. "
        "Pedido 1003 entregue. Nenhuma pendência."
    )
    return ModelResponse(parts=[TextPart(texto)])


with compactacao.resumidor.override(model=FunctionModel(modelo_resumidor)):
    historico = conversar(compactacao.agente_compacto)
print()
print(historico[0].parts[0].content)
