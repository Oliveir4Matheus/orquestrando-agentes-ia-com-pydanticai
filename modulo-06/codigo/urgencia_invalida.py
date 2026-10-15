from typing import Literal

from pydantic import BaseModel, ValidationError

from pydantic_ai import Agent

import modelos_simulados as sim


class Reclamacao(BaseModel):
    codigo_pedido: str | None
    problema: str
    urgencia: Literal["baixa", "media", "alta"]


dados = {"codigo_pedido": "1001", "problema": "atraso", "urgencia": "urgentíssima"}

try:
    Reclamacao(**dados)
except ValidationError as erro:
    print("Pydantic:", erro.errors()[0]["type"], erro.errors()[0]["loc"])

extrator = Agent(sim.saida(dados, "extrator"), output_type=Reclamacao)
try:
    extrator.run_sync("O pedido 1001 está atrasado!")
except Exception as erro:
    print("Agente:", type(erro).__name__)
print("chamadas ao modelo:", len(sim.CHAMADAS))
