from dataclasses import replace

from pydantic_ai import ModelMessage, ModelRequest
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.messages import ToolReturnPart, UserPromptPart

from atendimento import criar_agente
from sessao import conversar

TURNOS_RECENTES = 1


def inicio_do_turno(mensagens: list[ModelMessage], turnos: int) -> int:
    """Índice da mensagem em que começa o N-ésimo turno, contando do fim."""
    encontrados = 0
    for indice in range(len(mensagens) - 1, -1, -1):
        mensagem = mensagens[indice]
        if isinstance(mensagem, ModelRequest) and any(
            isinstance(parte, UserPromptPart) for parte in mensagem.parts
        ):
            encontrados += 1
            if encontrados == turnos:
                return indice
    return 0


def limpar_resultados(mensagens: list[ModelMessage]) -> list[ModelMessage]:
    corte = inicio_do_turno(mensagens, TURNOS_RECENTES + 1)
    limpas = []
    for indice, mensagem in enumerate(mensagens):
        if indice < corte and isinstance(mensagem, ModelRequest):
            partes = [
                replace(parte, content="[resultado omitido]")
                if isinstance(parte, ToolReturnPart)
                else parte
                for parte in mensagem.parts
            ]
            mensagem = replace(mensagem, parts=partes)
        limpas.append(mensagem)
    return limpas


agente_enxuto = criar_agente(capabilities=[ProcessHistory(limpar_resultados)])

if __name__ == "__main__":
    conversar(agente_enxuto)
