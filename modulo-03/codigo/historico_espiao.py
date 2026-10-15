from pydantic_ai import Agent, ModelMessage
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.models.test import TestModel


def espiar(mensagens: list[ModelMessage]) -> list[ModelMessage]:
    print(f"O modelo vai receber {len(mensagens)} mensagens")
    return mensagens


agente = Agent(TestModel(), capabilities=[ProcessHistory(espiar)])


@agente.tool_plain
def consultar_pedido(codigo: str) -> str:
    return "Pedido enviado."


resultado = agente.run_sync("Onde está o pedido 1001?")
print(f"Histórico final: {len(resultado.all_messages())} mensagens")
