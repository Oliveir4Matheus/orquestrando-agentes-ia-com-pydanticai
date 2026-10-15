from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def contar(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart(f"recebi {len(mensagens)} mensagem(ns)")])


atendente = Agent(FunctionModel(contar))

primeira = atendente.run_sync("Quanto custa o vaso de barro?")
print(primeira.output)

segunda = atendente.run_sync("E o de cerâmica?", message_history=primeira.all_messages())
print(segunda.output)
print("all_messages:", len(segunda.all_messages()))
print("new_messages:", len(segunda.new_messages()))

esquecida = atendente.run_sync("E o de cerâmica?")
print(esquecida.output)
