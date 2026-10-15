from dataclasses import dataclass

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO


class Avaliacao(BaseModel):
    problemas: list[str]
    aprovado: bool


@dataclass
class Resultado:
    texto: str
    aprovado: bool
    rodadas: int


redator = Agent(
    MODELO,
    instructions=(
        "Você escreve respostas a reclamações de clientes da Casa Verde: empáticas, "
        "claras, sem prometer o que a loja não confirmou."
    ),
)

avaliador = Agent(
    MODELO,
    output_type=Avaliacao,
    instructions=(
        "Avalie a resposta pelos critérios: (1) reconhece o problema com empatia; "
        "(2) informa um próximo passo concreto; (3) não promete reembolso nem prazo "
        "não confirmado; (4) tem no máximo quatro frases. Liste os problemas "
        "encontrados antes de decidir `aprovado`; aprove só se não houver nenhum."
    ),
)


def melhorar(reclamacao: str, max_rodadas: int = 3) -> Resultado:
    rascunho = redator.run_sync(reclamacao).output
    for rodada in range(1, max_rodadas + 1):
        avaliacao = avaliador.run_sync(f"Reclamação: {reclamacao}\nResposta: {rascunho}").output
        print(f"Rodada {rodada}: {'aprovado' if avaliacao.aprovado else 'reprovado'}")
        if avaliacao.aprovado:
            return Resultado(rascunho, True, rodada)
        for problema in avaliacao.problemas:
            print("  -", problema)
        problemas = "\n".join(f"- {p}" for p in avaliacao.problemas)
        rascunho = redator.run_sync(
            f"Reclamação: {reclamacao}\nSua resposta anterior: {rascunho}\n"
            f"Problemas apontados:\n{problemas}\nReescreva corrigindo os problemas."
        ).output
    return Resultado(rascunho, False, max_rodadas)
