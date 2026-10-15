from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

atendente = Agent(TestModel(), instructions="Você é o atendente da loja Casa Verde.")


@atendente.tool_plain
def consultar_preco(produto: str) -> float:
    """Devolve o preço de um produto da loja."""
    return 49.90


resultado = atendente.run_sync("Quanto custa o vaso de barro?")

for mensagem in resultado.all_messages():
    print(type(mensagem).__name__, mensagem.kind)
    for parte in mensagem.parts:
        print("   ", parte.part_kind)
