from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


class Status(BaseModel):
    codigo: str
    status: str


agente = Agent(TestModel(), output_type=Status)

resultado = agente.run_sync("Qual o status do pedido 1002?")
print(resultado.output)
print(type(resultado.output).__name__)
