import re

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

faq = Agent(TestModel(custom_output_text="resposta do faq"))
agente_de_pedidos = Agent(TestModel(custom_output_text="resposta do agente"))


def atender(mensagem: str) -> str:
    if re.search(r"\d{4}", mensagem):
        return agente_de_pedidos.run_sync(mensagem).output
    return faq.run_sync(mensagem).output


mensagens = [
    "Qual é o prazo para devolver um produto?",
    "Onde está o meu pedido 1001?",
    "Comprei em 2024 e o produto veio com defeito",
]
for mensagem in mensagens:
    print(f"{mensagem} -> {atender(mensagem)}")
