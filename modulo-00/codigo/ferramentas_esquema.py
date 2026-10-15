from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def mostrar_ferramentas(mensagens, info: AgentInfo) -> ModelResponse:
    for ferramenta in info.function_tools:
        print(ferramenta.name, "->", ferramenta.description)
        for nome, campo in ferramenta.parameters_json_schema["properties"].items():
            print("   ", nome, campo)
        print("    obrigatórios:", ferramenta.parameters_json_schema.get("required", []))
    return ModelResponse(parts=[TextPart("ok")])


atendente = Agent(FunctionModel(mostrar_ferramentas))


@atendente.tool_plain
def consultar_estoque(produto: str, loja: str = "centro") -> int:
    """Informa quantas unidades de um produto há em uma loja.

    Args:
        produto: nome do produto, como 'vaso de barro'.
        loja: unidade da Casa Verde onde procurar.
    """
    return 12


@atendente.tool
def etapa_atual(ctx: RunContext) -> int:
    """Diz em que etapa da execução o agente está."""
    return ctx.run_step


atendente.run_sync("Tem vaso de barro na loja do centro?")
