from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import RetryPromptPart, ToolReturnPart, UserPromptPart


def resumir_erro(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    return "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in conteudo)


def mostrar(resultado) -> None:
    for mensagem in resultado.all_messages():
        usa_ferramenta = isinstance(mensagem, ModelResponse) and any(
            isinstance(parte, ToolCallPart) for parte in mensagem.parts
        )
        for parte in mensagem.parts:
            if isinstance(parte, UserPromptPart):
                print("Pedido      :", parte.content)
            elif isinstance(parte, TextPart) and usa_ferramenta:
                print("Pensamento  :", parte.content)
            elif isinstance(parte, ToolCallPart):
                print("Ação        :", parte.tool_name, parte.args_as_dict())
            elif isinstance(parte, ToolReturnPart):
                print("Observação  :", parte.content)
            elif isinstance(parte, RetryPromptPart):
                print("Erro        :", resumir_erro(parte.content))
            elif isinstance(parte, TextPart):
                print("Resposta    :", parte.content)
