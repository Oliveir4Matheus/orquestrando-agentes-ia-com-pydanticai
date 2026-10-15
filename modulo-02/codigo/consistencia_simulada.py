from itertools import cycle

from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import consistencia
from cot import PERGUNTA, raciocinado

respostas = cycle([116.10, 116.10, 129.00, 116.10, 58.05])


def modelo_instavel(mensagens, info: AgentInfo) -> ModelResponse:
    nome = info.output_tools[0].name
    return ModelResponse(parts=[ToolCallPart(nome, {"passos": ["..."], "valor": next(respostas)})])


with raciocinado.override(model=FunctionModel(modelo_instavel)):
    valor, votos, valores = consistencia.votar(PERGUNTA)
print("Respostas:", valores)
print(f"Mais votada: R$ {valor:.2f} ({votos} de {len(valores)})")
