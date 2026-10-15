from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, SystemPromptPart, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def espiar(mensagens, info: AgentInfo) -> ModelResponse:
    sistema = [p.content for m in mensagens for p in m.parts if isinstance(p, SystemPromptPart)]
    print("  instructions:", info.instructions)
    print("  system_prompt:", sistema)
    return ModelResponse(parts=[TextPart("ok")])


com_instrucoes = Agent(FunctionModel(espiar), instructions="Seja o atendente da Casa Verde.")
com_sistema = Agent(FunctionModel(espiar), system_prompt="Seja o atendente da Casa Verde.")
revisor = Agent(FunctionModel(espiar), instructions="Revise o texto.")

for agente in [com_instrucoes, com_sistema]:
    print("primeira execução:")
    anterior = agente.run_sync("Oi")
    print("revisor com o histórico:")
    revisor.run_sync("Revise", message_history=anterior.all_messages())
