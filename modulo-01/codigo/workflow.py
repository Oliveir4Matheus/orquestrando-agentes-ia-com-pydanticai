import re

from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido

redator = Agent(
    MODELO,
    instructions=(
        "Escreva uma resposta cordial de até duas frases para o cliente "
        "usando apenas os dados do pedido recebidos."
    ),
)


def atender(mensagem: str) -> str:
    achado = re.search(r"\d{4}", mensagem)
    if achado is None:
        return "Não encontrei o número do pedido. Pode informá-lo?"

    pedido = buscar_pedido(achado.group())
    if pedido is None:
        return "Não localizei esse pedido."

    return redator.run_sync(f"Dados do pedido: {pedido}").output


print(atender("Onde está o meu pedido 1001?"))
print(atender("Cadê a minha cadeira? O pedido é o mil e dois."))
