from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def espiar(mensagens: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    for ferramenta in info.function_tools:
        print(ferramenta.name, "->", ferramenta.description)
        print(ferramenta.parameters_json_schema["properties"])
    return ModelResponse(parts=[TextPart("ok")])


agente = Agent(FunctionModel(espiar))


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código.

    Args:
        codigo: código do pedido, como '1002'.
    """
    return "enviado"


agente.run_sync("Onde está o pedido 1002?")
