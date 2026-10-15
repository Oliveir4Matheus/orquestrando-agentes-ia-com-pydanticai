from pydantic_ai import Agent

from config import MODELO

chatbot = Agent(
    MODELO,
    instructions="Você atende clientes da loja Casa Verde. Responda em até duas frases.",
)

resultado = chatbot.run_sync("Onde está o meu pedido 1001?")
print(resultado.output)
print("Chamadas ao modelo:", resultado.usage.requests)
