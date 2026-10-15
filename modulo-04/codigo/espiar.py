import json

from pydantic_ai import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def espiar_ferramentas(agente, **opcoes) -> None:
    """Mostra o contrato de cada ferramenta exatamente como o modelo o recebe."""

    def modelo_espiao(mensagens, info: AgentInfo) -> ModelResponse:
        for ferramenta in info.function_tools:
            print(f"{ferramenta.name} | {ferramenta.description}")
            print("  ", json.dumps(ferramenta.parameters_json_schema, ensure_ascii=False))
        return ModelResponse(parts=[TextPart("ok")])

    agente.run_sync("oi", model=FunctionModel(modelo_espiao), **opcoes)
