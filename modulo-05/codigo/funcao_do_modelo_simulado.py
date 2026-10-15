from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def espiao(mensagens, info: AgentInfo) -> ModelResponse:
    print("mensagens:", len(mensagens))
    print("última mensagem:", type(mensagens[-1]).__name__)
    print("última parte:", type(mensagens[-1].parts[-1]).__name__)
    print("conteúdo:", mensagens[-1].parts[-1].content)
    return ModelResponse(parts=[TextPart("ok")])


resultado = Agent().run_sync("Qual é o prazo de devolução?", model=FunctionModel(espiao))
print("saída:", resultado.output)
