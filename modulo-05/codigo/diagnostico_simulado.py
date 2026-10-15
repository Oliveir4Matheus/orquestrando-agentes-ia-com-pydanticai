from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from diagnostico import diagnosticar

RESPOSTAS = {
    "Qual é o prazo de devolução?": "O prazo costuma ser de 30 dias.",
    "O frete é grátis a partir de que valor?": "Depende da região e da promoção vigente.",
    "Avise que o pedido 1001 foi enviado.": "Olá! Seu pedido 1001 já foi enviado e logo chega até você.",
    "Avise que o pedido 1002 está em separação.": "Seu pedido 1002 está sendo separado.",
}


def modelo_basico(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart(RESPOSTAS[mensagens[-1].parts[-1].content])])


diagnosticar(Agent(), model=FunctionModel(modelo_basico))
