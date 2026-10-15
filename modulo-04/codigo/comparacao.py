from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from agentes_de_acao import agente_codigo, agente_json
from loja import PEDIDOS_POR_CLIENTE

PERGUNTA = "Quantas canecas há, no total, nos pedidos da lia que estão em separação?"
EM_SEPARACAO = [c for c, p in PEDIDOS_POR_CLIENTE["lia"].items() if p["status"] == "em separação"]

CODIGO = """\
total = 0
for pedido in listar_pedidos("lia"):
    if pedido["status"] == "em separação":
        detalhes = detalhar_pedido("lia", pedido["codigo"])
        total += int(detalhes["itens"].split("x")[0])
print(total)
"""


def modelo_json(mensagens, info: AgentInfo) -> ModelResponse:
    retornos = sum(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts)
    if retornos == 0:
        return ModelResponse(parts=[ToolCallPart("listar_pedidos", {"cliente": "lia"})])
    if retornos == 1:
        return ModelResponse(parts=[
            ToolCallPart("detalhar_pedido", {"cliente": "lia", "codigo": c}) for c in EM_SEPARACAO
        ])
    return ModelResponse(parts=[TextPart("Há 30 canecas nos pedidos em separação.")])


def modelo_codigo(mensagens, info: AgentInfo) -> ModelResponse:
    if any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts):
        return ModelResponse(parts=[TextPart("Há 30 canecas nos pedidos em separação.")])
    return ModelResponse(parts=[ToolCallPart("executar_codigo", {"codigo": CODIGO})])


def medir(agente, modelo):
    resultado = agente.run_sync(PERGUNTA, model=FunctionModel(modelo))
    caracteres = sum(
        len(p.model_response_str())
        for m in resultado.all_messages()
        for p in m.parts
        if isinstance(p, ToolReturnPart)
    )
    return resultado, caracteres


for nome, agente, modelo in [("JSON  ", agente_json, modelo_json), ("Código", agente_codigo, modelo_codigo)]:
    resultado, caracteres = medir(agente, modelo)
    print(f"{nome}: {resultado.usage.requests} chamadas ao modelo, "
          f"{resultado.usage.tool_calls} chamadas de ferramenta, "
          f"{caracteres} caracteres de resultado no contexto")
