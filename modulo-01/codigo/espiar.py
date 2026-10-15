from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from suporte import suporte


def espiar(mensagens, info: AgentInfo) -> ModelResponse:
    for ferramenta in info.function_tools:
        print(ferramenta.name, "->", ferramenta.description)
    return ModelResponse(parts=[TextPart("ok")])


suporte.run_sync("oi", model=FunctionModel(espiar))
