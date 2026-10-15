from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    return f"Pedido {codigo}: entregue."


def consultar_politica(tema: str) -> str:
    """Consulta uma política da loja. Temas: devolucao, cancelamento, frete."""
    return f"Política de {tema}."


modelo = TestModel(call_tools=[])
agente = Agent(modelo, tools=[consultar_pedido, consultar_politica])
agente.run_sync("oi")

for ferramenta in modelo.last_model_request_parameters.function_tools:
    print(ferramenta.name, "|", ferramenta.description)
    print("  parâmetros:", list(ferramenta.parameters_json_schema["properties"]))
