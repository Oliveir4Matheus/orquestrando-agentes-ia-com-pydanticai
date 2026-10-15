from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from rag import agente_rag
from trajetoria import mostrar


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    if any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts):
        return ModelResponse(parts=[TextPart(
            "Sim, você pode devolver em até 7 dias corridos após o recebimento, "
            "com o produto na embalagem original [devolucao]."
        )])
    return ModelResponse(parts=[
        TextPart("Vou consultar a política de devolução."),
        ToolCallPart("buscar_politicas", {"pergunta": "prazo para devolver o produto"}),
    ])


mostrar(agente_rag.run_sync("Posso devolver o produto?", model=FunctionModel(modelo_roteirizado)))
