from dataclasses import dataclass, field

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO
from rag import LIMIAR, indice


class Afirmacao(BaseModel):
    texto: str
    trecho_id: str | None


class Verificacao(BaseModel):
    afirmacoes: list[Afirmacao]


@dataclass
class Resposta:
    texto: str
    citacoes: list[str] = field(default_factory=list)
    suporte: float = 0.0
    revisada: bool = False


redator = Agent(
    MODELO,
    instructions=(
        "Responda ao cliente usando o contexto fornecido, citando o id do trecho "
        "entre colchetes. Seja breve."
    ),
)

verificador = Agent(
    MODELO,
    output_type=Verificacao,
    instructions=(
        "Divida a resposta em afirmações. Para cada afirmação, informe o id do "
        "trecho que a sustenta ou null se nenhum dos trechos fornecidos a sustenta. "
        "Considere apenas os trechos fornecidos, nunca o seu conhecimento próprio."
    ),
)

RECUSA = "Não encontrei essa informação nas políticas da loja. Posso encaminhar você a um atendente."


def suporte_de(verificacao: Verificacao) -> float:
    if not verificacao.afirmacoes:
        return 0.0
    apoiadas = sum(1 for a in verificacao.afirmacoes if a.trecho_id)
    return apoiadas / len(verificacao.afirmacoes)


def responder_ancorado(pergunta: str, minimo: float = 1.0) -> Resposta:
    achados = [(p, f) for p, f in indice.buscar(pergunta, k=2) if p >= LIMIAR]
    if not achados:
        return Resposta(RECUSA)

    contexto = "\n".join(f"[{f.id}] {f.texto}" for _, f in achados)
    rascunho = redator.run_sync(f"Contexto:\n{contexto}\n\nPergunta: {pergunta}").output
    verificacao = verificador.run_sync(f"Trechos:\n{contexto}\n\nResposta:\n{rascunho}").output
    suporte = suporte_de(verificacao)
    citacoes = sorted({a.trecho_id for a in verificacao.afirmacoes if a.trecho_id})

    if suporte >= minimo:
        return Resposta(rascunho, citacoes, suporte)

    apoiadas = [a.texto for a in verificacao.afirmacoes if a.trecho_id]
    if not apoiadas:
        return Resposta(RECUSA, [], suporte)
    return Resposta(" ".join(apoiadas), citacoes, suporte, revisada=True)
