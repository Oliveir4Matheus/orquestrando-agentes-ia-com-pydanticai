from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    ModelResponse,
    RunContext,
    TextPart,
    ToolCallPart,
    ToolDenied,
)
from pydantic_ai.models.function import FunctionModel


def modelo(mensagens, info):
    if len(mensagens) == 1:
        return ModelResponse(parts=[ToolCallPart("reembolsar", {"codigo": "1001", "valor": 250.0}, tool_call_id="chamada-1")])
    return ModelResponse(parts=[TextPart("Não foi possível reembolsar.")])


agente = Agent(FunctionModel(modelo), output_type=[str, DeferredToolRequests])


@agente.tool
def reembolsar(ctx: RunContext[None], codigo: str, valor: float) -> str:
    if not ctx.tool_call_approved:
        raise ApprovalRequired(metadata={"pedido": codigo, "valor": valor})
    return f"Reembolso de R$ {valor:.2f} registrado."


primeira = agente.run_sync("Reembolso do pedido 1001.")
pedidos = primeira.output
print("Tipo da saída:", type(pedidos).__name__)
print("Chamadas diretas:", pedidos.calls)
for chamada in pedidos.approvals:
    print("Pendente:", chamada.tool_name, chamada.args_as_dict(), chamada.tool_call_id)
    print("Metadados:", pedidos.metadata[chamada.tool_call_id])

decisoes = DeferredToolResults()
decisoes.approvals["chamada-1"] = ToolDenied("prazo de devolução expirado")
segunda = agente.run_sync(message_history=primeira.all_messages(), deferred_tool_results=decisoes)
print("Tipo da saída:", type(segunda.output).__name__)
print("Resposta:", segunda.output)
