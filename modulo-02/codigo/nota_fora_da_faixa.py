from pydantic import BaseModel, Field, ValidationError

from pydantic_ai import Agent, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.settings import ModelSettings


class Nota(BaseModel):
    justificativa: str
    nota: int = Field(ge=0, le=10)


try:
    Nota(justificativa="Custo alto.", nota=11)
except ValidationError as erro:
    print(erro.errors()[0]["msg"])

print(ModelSettings(thinking="high"))

chamadas = []


def modelo_distraido(mensagens, info: AgentInfo) -> ModelResponse:
    chamadas.append(len(mensagens))
    nota = 11 if len(chamadas) == 1 else 8
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
        "justificativa": "Resolve sem violar o prazo.", "nota": nota,
    })])


avaliador = Agent(FunctionModel(modelo_distraido), output_type=Nota)
resultado = avaliador.run_sync("Caso: sofá manchado")
print("Chamadas ao modelo:", len(chamadas))
print("Nota final:", resultado.output.nota)
