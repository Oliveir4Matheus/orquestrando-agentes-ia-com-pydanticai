from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

CATALOGO = {"vaso de barro", "terra adubada", "regador"}
TENTATIVAS = [
    {"produto": "vaso de barro", "quantidade": 0},
    {"produto": "vaso", "quantidade": 3},
    {"produto": "vaso de barro", "quantidade": 3},
]


class Pedido(BaseModel):
    produto: str
    quantidade: int = Field(gt=0)


def modelo_desastrado(mensagens, info: AgentInfo) -> ModelResponse:
    ultima = mensagens[-1].parts[-1]
    if ultima.part_kind == "retry-prompt":
        erro = ultima.content
        print("  correção pedida:", erro[0]["msg"] if isinstance(erro, list) else erro)
    numero = sum(1 for mensagem in mensagens if mensagem.kind == "response")
    return ModelResponse(parts=[ToolCallPart("final_result", TENTATIVAS[numero])])


for limite in (1, 2):
    extrator = Agent(FunctionModel(modelo_desastrado), output_type=Pedido, retries=limite)

    @extrator.output_validator
    def produto_existe(pedido: Pedido) -> Pedido:
        if pedido.produto not in CATALOGO:
            raise ModelRetry(f"'{pedido.produto}' não está no catálogo.")
        return pedido

    print(f"retries={limite}")
    try:
        print("  saída:", extrator.run_sync("Quero 3 vasos de barro.").output)
    except UnexpectedModelBehavior as erro:
        print("  falhou:", erro)
