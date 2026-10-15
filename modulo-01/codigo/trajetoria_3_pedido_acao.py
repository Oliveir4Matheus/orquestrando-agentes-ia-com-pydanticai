from pydantic_ai import ToolCallPart
from pydantic_ai.messages import UserPromptPart
from pydantic_ai.models.function import FunctionModel

from agente import agente
from modelo_roteirizado import modelo_roteirizado

resultado = agente.run_sync(
    "Compare os pedidos 1001 e 1002.", model=FunctionModel(modelo_roteirizado)
)

for mensagem in resultado.all_messages():
    for parte in mensagem.parts:
        if isinstance(parte, UserPromptPart):
            print("Pedido     :", parte.content)
        elif isinstance(parte, ToolCallPart):
            print("Ação       :", parte.tool_name, parte.args_as_dict())
