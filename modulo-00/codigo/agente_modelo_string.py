from pydantic_ai import Agent
from pydantic_ai.exceptions import UserError

MODELO = "test"  # no livro: "anthropic:claude-sonnet-5-5"

agente = Agent(MODELO, instructions="Responda em português.")
print(agente.model.system)
print(agente.run_sync("Olá").output)

for nome in ["anthropic:claude-sonnet-5-5", "casaverde:modelo-1"]:
    try:
        Agent(nome)
    except UserError as erro:
        print(nome, "->", str(erro)[:60])
