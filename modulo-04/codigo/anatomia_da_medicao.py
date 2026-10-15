from pydantic_ai import Agent, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

agente = Agent(instructions="Some os números pedidos.")


@agente.tool_plain
def somar(a: int, b: int) -> dict:
    return {"total": a + b}


def modelo(mensagens, info: AgentInfo) -> ModelResponse:
    if any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts):
        return ModelResponse(parts=[TextPart("Deu 5.")])
    return ModelResponse(parts=[ToolCallPart("somar", {"a": 2, "b": 3})])


resultado = agente.run_sync("Some 2 e 3.", model=FunctionModel(modelo))

for mensagem in resultado.all_messages():
    for parte in mensagem.parts:
        print(type(parte).__name__)
        if isinstance(parte, ToolReturnPart):
            print("  content            =", parte.content)
            print("  model_response_str =", parte.model_response_str())

print(resultado.usage.requests, resultado.usage.tool_calls)
