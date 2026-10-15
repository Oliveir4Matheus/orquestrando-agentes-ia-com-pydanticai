from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.test import TestModel

agente = Agent(TestModel(call_tools=["consultar_pedido"]))


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido."""
    raise ModelRetry("Código inválido. Envie só os 4 dígitos, como 1001.")


try:
    agente.run_sync("Cadê o meu pedido #1001?")
except UnexpectedModelBehavior as erro:
    print("Falhou:", erro)
