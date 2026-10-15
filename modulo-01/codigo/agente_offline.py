from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from loja import buscar_pedido

agente = Agent(TestModel(call_tools=["consultar_pedido"]))


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


resultado = agente.run_sync("Onde está o meu pedido 1001?")
print("Chamadas ao modelo:", resultado.usage.requests)
print("Chamadas de ferramenta:", resultado.usage.tool_calls)
print("Resposta:", resultado.output)
