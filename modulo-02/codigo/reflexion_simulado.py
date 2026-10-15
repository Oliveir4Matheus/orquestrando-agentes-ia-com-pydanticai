from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import reflexion


def modelo_ator(mensagens, info: AgentInfo) -> ModelResponse:
    prompt = mensagens[-1].parts[0].content
    if "Lições de tentativas anteriores" in prompt:
        texto = "Seu pedido 1002 está em separação e chega em 15/10. Equipe Casa Verde"
    else:
        texto = "Seu pedido 1002 está em separação e chega em 15/10."
    return ModelResponse(parts=[TextPart(texto)])


def modelo_reflexor(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart("Termine toda mensagem com a assinatura 'Equipe Casa Verde'.")])


with reflexion.ator.override(model=FunctionModel(modelo_ator)), \
        reflexion.reflexor.override(model=FunctionModel(modelo_reflexor)):
    reflexion.resolver()
