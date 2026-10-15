import asyncio
import tempfile
from pathlib import Path

from pydantic_ai import Agent, ModelResponse, RunContext, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from config import MODELO
from execucao_duravel import executar_com_checkpoint
from idempotencia import Livro

EFEITOS: list[int] = []  # cada execução real de uma etapa deixa um rastro aqui
API = {"fora_do_ar": True}
LIVRO: dict[str, Livro | None] = {"atual": None}

agente = Agent(MODELO)


@agente.tool
def etapa(ctx: RunContext[None], numero: int) -> str:
    """Executa uma etapa do processo (com efeito no mundo)."""

    def efeito() -> str:
        EFEITOS.append(numero)
        return f"etapa {numero} concluída"

    livro = LIVRO["atual"]
    return livro.executar_uma_vez(ctx.tool_call_id, efeito) if livro else efeito()


def modelo(mensagens, info):
    concluidas = sum(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts)
    if concluidas == 2 and API["fora_do_ar"]:
        raise ConnectionError("a API do modelo caiu")
    if concluidas < 3:
        return ModelResponse(parts=[ToolCallPart("etapa", {"numero": concluidas + 1})])
    return ModelResponse(parts=[TextPart("As três etapas foram concluídas.")])


async def com_queda(titulo: str, executar):
    EFEITOS.clear()
    API["fora_do_ar"] = True
    print(f"== {titulo}")
    try:
        await executar()
    except ConnectionError as erro:
        print("  queda:", erro)
    API["fora_do_ar"] = False
    resposta = await executar()
    print("  resposta:", resposta if isinstance(resposta, str) else resposta.output)
    print("  etapas executadas:", EFEITOS)


async def principal():
    pergunta = "Execute as três etapas do processo."
    modelo_simulado = FunctionModel(modelo)

    await com_queda(
        "1. Sem checkpoint: recomeça do zero",
        lambda: agente.run(pergunta, model=modelo_simulado),
    )

    pasta = Path(tempfile.mkdtemp())
    await com_queda(
        "2. Com checkpoint: retoma, mas a etapa 2 se repete",
        lambda: executar_com_checkpoint(agente, pergunta, pasta / "a.json", model=modelo_simulado),
    )

    LIVRO["atual"] = Livro(pasta / "efeitos.json")
    await com_queda(
        "3. Com checkpoint e registro de efeitos: cada etapa acontece uma vez",
        lambda: executar_com_checkpoint(agente, pergunta, pasta / "b.json", model=modelo_simulado),
    )


asyncio.run(principal())
