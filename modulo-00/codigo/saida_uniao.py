from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class Pedido(BaseModel):
    """Use quando o cliente quer comprar."""

    produto: str
    quantidade: int


class Reclamacao(BaseModel):
    """Use quando o cliente relata um problema."""

    motivo: str


def modelo_triagem(mensagens, info: AgentInfo) -> ModelResponse:
    print("menu:", [ferramenta.name for ferramenta in info.output_tools], "| texto livre:", info.allow_text_output)
    pergunta = mensagens[0].parts[-1].content
    if "quebrado" in pergunta:
        return ModelResponse(parts=[ToolCallPart("final_result_Reclamacao", {"motivo": "vaso quebrado"})])
    if "quero" in pergunta:
        return ModelResponse(parts=[ToolCallPart("final_result_Pedido", {"produto": "regador", "quantidade": 2})])
    return ModelResponse(parts=[TextPart("Abrimos às 8h.")])


triagem = Agent(FunctionModel(modelo_triagem), output_type=[Pedido, Reclamacao, str])

for pergunta in ("quero 2 regadores", "o vaso chegou quebrado", "que horas vocês abrem?"):
    saida = triagem.run_sync(pergunta).output
    print(" ", type(saida).__name__, "->", saida)



def modelo_sugestoes(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart("final_result", {"response": ["regador", "terra adubada"]})])


lista = Agent(FunctionModel(modelo_sugestoes), output_type=list[str])
print(lista.run_sync("Sugira dois produtos.").output)
