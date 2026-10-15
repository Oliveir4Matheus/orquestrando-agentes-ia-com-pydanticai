from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, RetryPromptPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class Produto(BaseModel):
    nome: str = Field(min_length=3)
    preco: float = Field(gt=0)


def modelo_falso(mensagens: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    ferramenta = info.output_tools[0]
    if len(mensagens) == 1:
        print("esquema recebido:", ferramenta.parameters_json_schema["required"])
        argumentos = '{"nome": "Vaso", "preco": -1}'
    else:
        erro = mensagens[-1].parts[0]
        assert isinstance(erro, RetryPromptPart)
        print("erro devolvido:", erro.content[0]["type"])
        argumentos = '{"nome": "Vaso", "preco": 49.9}'
    return ModelResponse(parts=[ToolCallPart(ferramenta.name, argumentos)])


agente = Agent(FunctionModel(modelo_falso), output_type=Produto)
resultado = agente.run_sync("Cadastre o vaso.")
print(repr(resultado.output))
