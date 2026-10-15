from pydantic_ai import Agent, ModelRetry, capture_run_messages
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def modelo_roteirizado(mensagens, info: AgentInfo) -> ModelResponse:
    print("ferramentas:", [ferramenta.name for ferramenta in info.function_tools])
    ultima = mensagens[-1].parts[-1]
    if ultima.part_kind == "user-prompt":
        return ModelResponse(parts=[ToolCallPart("consultar_preco", {"produto": "vaso"})])
    if ultima.part_kind == "retry-prompt":
        print("o agente reclamou:", ultima.content)
        return ModelResponse(parts=[ToolCallPart("consultar_preco", '{"produto": "vaso de barro"}')])
    return ModelResponse(parts=[TextPart(f"O vaso de barro custa R$ {ultima.content}.")])


atendente = Agent(FunctionModel(modelo_roteirizado))


@atendente.tool_plain
def consultar_preco(produto: str) -> float:
    """Devolve o preço de um produto da loja."""
    if produto != "vaso de barro":
        raise ModelRetry("Produto desconhecido. Use o nome completo, como 'vaso de barro'.")
    return 49.90


with capture_run_messages() as mensagens:
    resultado = atendente.run_sync("Quanto custa o vaso?")

print(resultado.output)
print([parte.part_kind for mensagem in mensagens for parte in mensagem.parts])
segunda_chamada = mensagens[3].parts[0]
print(repr(segunda_chamada.args), segunda_chamada.args_as_dict())
