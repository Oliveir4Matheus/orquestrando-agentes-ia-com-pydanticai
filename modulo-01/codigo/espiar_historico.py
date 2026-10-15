from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.messages import UserPromptPart
from pydantic_ai.models.function import AgentInfo


def espiar_historico(mensagens, info: AgentInfo) -> ModelResponse:
    perguntas = [
        parte.content
        for mensagem in mensagens
        for parte in mensagem.parts
        if isinstance(parte, UserPromptPart)
    ]
    print("O modelo está vendo:", perguntas)
    return ModelResponse(parts=[TextPart("ok")])
