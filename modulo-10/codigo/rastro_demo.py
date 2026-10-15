from pydantic_ai import Agent, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from config import MODELO
from loja import buscar_pedido
from rastro import arvore_do_rastro

agente = Agent(MODELO, name="atendente")


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido."""
    return str(buscar_pedido(codigo))


def modelo(mensagens, info):
    if any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts):
        return ModelResponse(parts=[TextPart("Seu pedido 1001 foi enviado.")])
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1001"})])


agente.run_sync("Onde está o pedido 1001?", model=FunctionModel(modelo))
for linha in arvore_do_rastro():
    print(linha)
