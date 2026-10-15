from pydantic_ai import Agent, Tool
from pydantic_ai.models.test import TestModel


def preco(produto: str) -> float:
    return 49.90


def frete(cep: str) -> float:
    """Calcula o frete de entrega para um CEP."""
    return 15.00


ferramenta_preco = Tool(preco, name="consultar_preco", description="Devolve o preço de um produto da Casa Verde.")
atendente = Agent(TestModel(), tools=[ferramenta_preco])
atendente.tool_plain(frete)

resultado = atendente.run_sync("Quanto custa o vaso com entrega?")
for mensagem in resultado.all_messages():
    if mensagem.kind == "response":
        for chamada in mensagem.tool_calls:
            print("pediu:", chamada.tool_name, chamada.args)
print(resultado.output)
