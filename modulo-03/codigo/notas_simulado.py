import tempfile
from pathlib import Path

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from notas import Caderno, agente


def primeira_sessao(mensagens, info: AgentInfo) -> ModelResponse:
    if isinstance(mensagens[-1].parts[-1], ToolReturnPart):
        return ModelResponse(parts=[TextPart("Combinado: reenviaremos o pedido 1002 em 20/10.")])
    return ModelResponse(parts=[ToolCallPart("anotar", {
        "texto": "Cliente Lia: reenvio do pedido 1002 combinado para 20/10, entregar à tarde."
    })])


def segunda_sessao(mensagens, info: AgentInfo) -> ModelResponse:
    print("Instruções recebidas pelo modelo:")
    print(mensagens[-1].instructions)
    return ModelResponse(parts=[TextPart("O reenvio do pedido 1002 está marcado para 20/10, à tarde.")])


caderno = Caderno(Path(tempfile.mkdtemp()) / "notas.json")

print("== Sessão 1")
print(agente.run_sync("Preciso que reenviem o pedido 1002 no dia 20, à tarde.",
                      model=FunctionModel(primeira_sessao), deps=caderno).output)

print("\n== Sessão 2 (histórico vazio)")
print(agente.run_sync("Quando vai ser o reenvio?",
                      model=FunctionModel(segunda_sessao), deps=caderno).output)
