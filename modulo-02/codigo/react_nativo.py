from pydantic_ai import Agent

from config import MODELO
from consulta import consultar_pedido, consultar_politica
from trajetoria import mostrar

agente = Agent(
    MODELO,
    tools=[consultar_pedido, consultar_politica],
    instructions=(
        "Você atende clientes da loja Casa Verde. Antes de cada chamada de "
        "ferramenta, escreva uma frase explicando por que vai chamá-la. "
        "Nunca invente dados. Responda em até três frases."
    ),
)

if __name__ == "__main__":
    resultado = agente.run_sync("Meu pedido 1003 chegou com defeito. Ainda consigo devolver?")
    mostrar(resultado)
