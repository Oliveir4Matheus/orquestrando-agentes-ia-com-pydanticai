from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class Pedido(BaseModel):
    """Pedido extraído da mensagem do cliente."""

    produto: str
    quantidade: int = Field(gt=0)


def modelo_extrator(mensagens, info: AgentInfo) -> ModelResponse:
    print("aceita texto?", info.allow_text_output)
    for ferramenta in info.output_tools:
        print("ferramenta de saída:", ferramenta.name, "-", ferramenta.description)
    return ModelResponse(parts=[ToolCallPart("final_result", {"produto": "vaso de barro", "quantidade": "3"})])


extrator = Agent(FunctionModel(modelo_extrator), output_type=Pedido)
resultado = extrator.run_sync("Quero 3 vasos de barro.")

print(repr(resultado.output))
print(resultado.output.quantidade * 49.90)
