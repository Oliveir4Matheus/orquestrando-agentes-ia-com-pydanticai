from pydantic_ai import TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart, UserPromptPart


def mostrar(resultado) -> None:
    for mensagem in resultado.all_messages():
        for parte in mensagem.parts:
            if isinstance(parte, UserPromptPart):
                print("Pedido     :", parte.content)
            elif isinstance(parte, ToolCallPart):
                print("Ação       :", parte.tool_name, parte.args_as_dict())
            elif isinstance(parte, ToolReturnPart):
                print("Observação :", parte.content)
            elif isinstance(parte, TextPart):
                print("Resposta   :", parte.content)
