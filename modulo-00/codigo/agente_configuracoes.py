from pydantic_ai import Agent, ModelSettings
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def espiar(mensagens, info: AgentInfo) -> ModelResponse:
    print("configurações recebidas:", info.model_settings)
    return ModelResponse(parts=[TextPart("ok")])


atendente = Agent(
    FunctionModel(espiar),
    model_settings=ModelSettings(temperature=0.7, max_tokens=300),
)

atendente.run_sync("Sugira um vaso")
atendente.run_sync("Sugira um vaso", model_settings=ModelSettings(temperature=0.0))
