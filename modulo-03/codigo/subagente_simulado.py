from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import subagente


def modelo_investigador(mensagens, info: AgentInfo) -> ModelResponse:
    retornos = sum(
        isinstance(parte, ToolReturnPart) for m in mensagens for parte in m.parts
    )
    if retornos == 0:
        return ModelResponse(parts=[ToolCallPart("listar_pedidos", {"cliente": "lia"})])
    if retornos == 1:
        return ModelResponse(parts=[ToolCallPart("detalhar_pedido", {"cliente": "lia", "codigo": "2002"})])
    if retornos == 2:
        return ModelResponse(parts=[ToolCallPart("detalhar_pedido", {"cliente": "lia", "codigo": "2006"})])
    return ModelResponse(parts=[TextPart("Os pedidos 2002 e 2006 estão em separação.")])


def modelo_principal(mensagens, info: AgentInfo) -> ModelResponse:
    if isinstance(mensagens[-1].parts[-1], ToolReturnPart):
        return ModelResponse(parts=[TextPart("Dois pedidos seus estão em separação: 2002 e 2006.")])
    return ModelResponse(parts=[ToolCallPart("investigar_historico", {"pergunta": "Quais pedidos estão em separação?"})])


with subagente.investigador.override(model=FunctionModel(modelo_investigador)):
    resultado = subagente.principal.run_sync(
        "Quais dos meus pedidos ainda estão em separação?",
        model=FunctionModel(modelo_principal),
    )
print(resultado.output)
