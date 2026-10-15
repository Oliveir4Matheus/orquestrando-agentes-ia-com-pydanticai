from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput, PromptedOutput, ToolOutput
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class Pedido(BaseModel):
    """Pedido extraído da mensagem do cliente."""

    produto: str
    quantidade: int


def modelo(mensagens, info: AgentInfo) -> ModelResponse:
    parametros = info.model_request_parameters
    print("modo:", parametros.output_mode)
    if info.output_tools:
        print("  ferramenta:", info.output_tools[0].name)
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"produto": "regador", "quantidade": 1})])
    if info.instructions:
        print("  instrução:", info.instructions.splitlines()[0])
    else:
        print("  esquema enviado à parte:", parametros.output_object.name)
    return ModelResponse(parts=[TextPart('{"produto": "regador", "quantidade": 1}')])


for tipo in (ToolOutput(Pedido, name="registrar_pedido"), NativeOutput(Pedido), PromptedOutput(Pedido)):
    agente = Agent(FunctionModel(modelo), output_type=tipo)
    print("  saída:", agente.run_sync("Quero um regador.").output)
