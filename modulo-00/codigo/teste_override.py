import os

from pydantic_ai import Agent, models
from pydantic_ai.models.test import TestModel

os.environ["ANTHROPIC_API_KEY"] = "chave-falsa"  # só para criar o agente; nada é enviado
models.ALLOW_MODEL_REQUESTS = False

atendente = Agent("anthropic:claude-sonnet-5-5", instructions="Você é o atendente da Casa Verde.")


def responder(pergunta: str) -> str:
    return atendente.run_sync(pergunta).output


try:
    responder("Quanto custa o vaso de barro?")
except RuntimeError as erro:
    print("bloqueado:", erro)

with atendente.override(model=TestModel(custom_output_text="O vaso custa R$ 49,90.")):
    print("no teste:", responder("Quanto custa o vaso de barro?"))

print("depois:", atendente.model.model_name)
