from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

modelo = TestModel(custom_output_text="O vaso de barro custa R$ 49,90.")

atendente = Agent(
    modelo,
    instructions="Você é o atendente da loja Casa Verde. Responda em uma frase.",
    name="atendente",
)

resultado = atendente.run_sync("Quanto custa o vaso de barro?")
print(resultado.output)
print(resultado.usage)

uso = resultado.usage
print("requisições:", uso.requests)
print("tokens de entrada:", uso.input_tokens)
print("tokens de saída:", uso.output_tokens)
print("total:", uso.total_tokens)
