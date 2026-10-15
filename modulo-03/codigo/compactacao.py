from dataclasses import replace

from pydantic_ai import Agent, ModelMessage, ModelRequest, ModelResponse, TextPart
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.messages import ToolReturnPart, UserPromptPart

from atendimento import criar_agente
from config import MODELO
from limpeza import inicio_do_turno
from sessao import conversar

LIMITE_MENSAGENS = 8
MANTER_TURNOS = 2

resumidor = Agent(
    MODELO,
    instructions=(
        "Resuma a conversa de atendimento abaixo para que outro atendente possa "
        "continuar. Preserve os códigos de pedido citados, os status e datas "
        "informados, pedidos do cliente ainda sem resposta e decisões tomadas. "
        "Descarte cumprimentos e dados repetidos. Use no máximo 6 linhas."
    ),
)


def transcrever(mensagens: list[ModelMessage]) -> str:
    linhas = []
    for mensagem in mensagens:
        for parte in mensagem.parts:
            if isinstance(parte, UserPromptPart):
                linhas.append(f"Cliente: {parte.content}")
            elif isinstance(parte, ToolReturnPart):
                linhas.append(f"Sistema: {str(parte.content).splitlines()[0]}")
            elif isinstance(parte, TextPart):
                linhas.append(f"Atendente: {parte.content}")
    return "\n".join(linhas)


async def compactar(mensagens: list[ModelMessage]) -> list[ModelMessage]:
    if len(mensagens) <= LIMITE_MENSAGENS:
        return mensagens
    corte = inicio_do_turno(mensagens, MANTER_TURNOS)
    if corte == 0:
        return mensagens

    resumo = (await resumidor.run(transcrever(mensagens[:corte]))).output
    primeira = mensagens[corte]
    nota = UserPromptPart(f"[Resumo da conversa até aqui]\n{resumo}")
    return [replace(primeira, parts=[nota, *primeira.parts])] + mensagens[corte + 1 :]


agente_compacto = criar_agente(capabilities=[ProcessHistory(compactar)])

if __name__ == "__main__":
    conversar(agente_compacto)
