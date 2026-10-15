import re

from pydantic_ai import Agent

from agente import agente as agente_de_pedidos
from config import MODELO

faq = Agent(
    MODELO,
    instructions=(
        "Você responde dúvidas gerais da loja Casa Verde: o prazo de devolução "
        "é de 7 dias após o recebimento e o frete é grátis acima de R$ 200. "
        "Responda em até duas frases."
    ),
)


def atender(mensagem: str) -> str:
    if re.search(r"\d{4}", mensagem):
        return agente_de_pedidos.run_sync(mensagem).output
    return faq.run_sync(mensagem).output


if __name__ == "__main__":
    print(atender("Qual é o prazo para devolver um produto?"))
    print(atender("Onde está o meu pedido 1001?"))
