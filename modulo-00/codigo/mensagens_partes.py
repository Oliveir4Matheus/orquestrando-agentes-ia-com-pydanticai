from pydantic_ai import Agent
from pydantic_ai.messages import TextPart, ToolCallPart, ToolReturnPart, UserPromptPart
from pydantic_ai.models.test import TestModel

atendente = Agent(TestModel(), instructions="Você é o atendente da loja Casa Verde.")


@atendente.tool_plain
def consultar_preco(produto: str) -> float:
    """Devolve o preço de um produto da loja."""
    return 49.90


resultado = atendente.run_sync("Quanto custa o vaso de barro?")

for mensagem in resultado.all_messages():
    for parte in mensagem.parts:
        if isinstance(parte, UserPromptPart):
            print("pergunta:", parte.content)
        elif isinstance(parte, ToolCallPart):
            print("chamada:", parte.tool_name, parte.args_as_dict(), parte.tool_call_id)
        elif isinstance(parte, ToolReturnPart):
            print("retorno:", parte.tool_name, parte.content, parte.tool_call_id)
        elif isinstance(parte, TextPart):
            print("texto:", parte.content)
