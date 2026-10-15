from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def modelo_espiao(mensagens, info: AgentInfo) -> ModelResponse:
    print("Mensagens recebidas:", len(mensagens))
    ultima = mensagens[-1]
    print("Tipo da última:", type(ultima).__name__)
    print("Partes:", [type(parte).__name__ for parte in ultima.parts])
    print("Conteúdo:", ultima.parts[0].content)
    return ModelResponse(parts=[TextPart("ok")])


agente = Agent(FunctionModel(modelo_espiao), instructions="Seja breve.")
print(agente.run_sync("Olá, loja").output)
