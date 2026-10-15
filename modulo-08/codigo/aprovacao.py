import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolDenied,
)

from config import MODELO
from risco import Acao, Camada, classificar

REGISTRO: list[dict] = []


def registrar(decisao: str, quem: str, motivo: str, acao: str) -> None:
    REGISTRO.append({
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "acao": acao,
        "decisao": decisao,
        "revisor": quem,
        "motivo": motivo,
    })


agente = Agent(
    MODELO,
    name="atendente",
    output_type=[str, DeferredToolRequests],
    instructions=(
        "Você atende clientes da Casa Verde. Para reembolsos, use `reembolsar`. "
        "Explique ao cliente o resultado em uma frase."
    ),
)


@agente.tool
def reembolsar(ctx: RunContext[None], codigo: str, valor: float) -> str:
    """Reembolsa um valor em um pedido."""
    camada = classificar(Acao("reembolsar", escreve=True, reversivel=False, valor=valor))
    if camada is Camada.APROVAR and not ctx.tool_call_approved:
        raise ApprovalRequired(metadata={"pedido": codigo, "valor": valor, "camada": camada.value})
    if camada is Camada.NOTIFICAR:
        registrar("notificado", "sistema", "dentro do limite de alçada", f"reembolsar {codigo} R$ {valor:.2f}")
    return f"Reembolso de R$ {valor:.2f} registrado para o pedido {codigo}."


@dataclass
class PedidoDeRevisao:
    id_da_chamada: str
    acao: str
    argumentos: dict
    impacto: str
    resumo_da_conversa: str


def montar_pedido(chamada, metadata: dict, conversa: str) -> PedidoDeRevisao:
    valor = metadata.get("valor", 0)
    return PedidoDeRevisao(
        id_da_chamada=chamada.tool_call_id,
        acao=chamada.tool_name,
        argumentos=chamada.args_as_dict(),
        impacto=f"Saída financeira de R$ {valor:.2f}, irreversível.",
        resumo_da_conversa=conversa,
    )


async def decidir(pedido: PedidoDeRevisao, revisores: list, espera: float):
    """Pergunta a cada revisor, em ordem, com prazo. Sem decisão: nega por padrão."""
    for revisor in revisores:
        try:
            aprovado, motivo = await asyncio.wait_for(revisor["decidir"](pedido), timeout=espera)
        except asyncio.TimeoutError:
            registrar("sem resposta", revisor["nome"], f"prazo de {espera} s esgotado", pedido.acao)
            continue
        registrar("aprovado" if aprovado else "negado", revisor["nome"], motivo, pedido.acao)
        return aprovado, motivo
    registrar("negado", "sistema", "nenhum revisor respondeu; padrão seguro", pedido.acao)
    return False, "nenhum revisor respondeu a tempo"


async def atender(mensagem: str, revisores: list, espera: float = 0.2, model=None) -> str:
    resultado = await agente.run(mensagem, model=model)
    while isinstance(resultado.output, DeferredToolRequests):
        pedidos = resultado.output
        decisoes = DeferredToolResults()
        for chamada in pedidos.approvals:
            pedido = montar_pedido(chamada, pedidos.metadata.get(chamada.tool_call_id, {}), mensagem)
            aprovado, motivo = await decidir(pedido, revisores, espera)
            decisoes.approvals[chamada.tool_call_id] = True if aprovado else ToolDenied(motivo)
        resultado = await agente.run(
            message_history=resultado.all_messages(), deferred_tool_results=decisoes, model=model
        )
    return resultado.output
