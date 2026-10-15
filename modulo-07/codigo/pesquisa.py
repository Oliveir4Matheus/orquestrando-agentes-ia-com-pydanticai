import asyncio

from pydantic import BaseModel

from pydantic_ai import Agent, RunContext

from config import MODELO, MODELO_RAPIDO
from dados_atraso import ESTOQUE, RECLAMACOES, TRANSPORTADORAS


class Briefing(BaseModel):
    """Instruções completas para um subagente, para que ele não precise adivinhar."""

    objetivo: str
    fonte: str
    formato_da_saida: str
    limite: str


def ler_transportadoras() -> str:
    """Entregas e atrasos de setembro por transportadora."""
    return "\n".join(f"{n}: {d['atrasos']} atrasos em {d['entregas']} entregas" for n, d in TRANSPORTADORAS.items())


def ler_estoque() -> str:
    """Rupturas de estoque em setembro por produto."""
    return "\n".join(f"{n}: {d['rupturas_em_setembro']} rupturas" for n, d in ESTOQUE.items())


def ler_reclamacoes() -> str:
    """Reclamações de clientes em setembro por motivo."""
    return "\n".join(f"{n}: {q}" for n, q in RECLAMACOES.items())


FERRAMENTAS_POR_FONTE = {
    "transportadoras": ler_transportadoras,
    "estoque": ler_estoque,
    "reclamacoes": ler_reclamacoes,
}

subagente = Agent(
    MODELO_RAPIDO,
    name="subagente",
    instructions="Cumpra o briefing recebido, usando só a fonte indicada, e devolva apenas o formato pedido.",
)

lider = Agent(
    MODELO,
    name="lider",
    instructions=(
        "Você investiga problemas operacionais da Casa Verde. Escale o esforço à "
        "complexidade: pergunta simples, nenhum subagente; comparação, de 2 a 4; "
        "investigação ampla, mais. Delegue com `delegar`, escrevendo para cada "
        "subagente um briefing completo (objetivo, fonte, formato da saída e limite) "
        "e sem sobreposição entre eles. Ao final, escreva um relatório de até 5 linhas."
    ),
)


@lider.tool
async def delegar(ctx: RunContext[None], briefing: Briefing) -> str:
    """Delega uma investigação focada a um subagente. Fontes: transportadoras, estoque, reclamacoes."""
    ferramenta = FERRAMENTAS_POR_FONTE.get(briefing.fonte)
    if ferramenta is None:
        return f"Fonte desconhecida: {briefing.fonte}."
    dados = ferramenta()
    resposta = await subagente.run(
        f"Objetivo: {briefing.objetivo}\nFormato: {briefing.formato_da_saida}\n"
        f"Limite: {briefing.limite}\nDados:\n{dados}",
        usage=ctx.usage,
    )
    return resposta.output
