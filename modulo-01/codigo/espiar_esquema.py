import json

from pydantic_ai import Agent, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from loja import buscar_pedido


def espiar(mensagens, info: AgentInfo) -> ModelResponse:
    ferramenta = info.function_tools[0]
    print(ferramenta.name)
    print(json.dumps(ferramenta.parameters_json_schema, indent=2))
    return ModelResponse(parts=[TextPart("ok")])


agente = Agent(FunctionModel(espiar))


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


agente.run_sync("oi")
