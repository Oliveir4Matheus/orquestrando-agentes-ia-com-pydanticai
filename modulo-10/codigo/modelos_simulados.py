import asyncio

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

CHAMADAS: list[str] = []


def prompt_do_usuario(mensagens) -> str:
    return mensagens[-1].parts[-1].content


def _valor(fonte, mensagens):
    return fonte(mensagens) if callable(fonte) else fonte


def texto(resposta, nome: str = "modelo", espera: float = 0.0) -> FunctionModel:
    """Modelo simulado que responde com texto. `resposta` é um texto ou uma função das mensagens."""

    async def modelo(mensagens, info: AgentInfo) -> ModelResponse:
        CHAMADAS.append(nome)
        if espera:
            await asyncio.sleep(espera)
        return ModelResponse(parts=[TextPart(_valor(resposta, mensagens))])

    return FunctionModel(modelo)


def saida(dados, nome: str = "modelo", espera: float = 0.0, tipo: str | None = None) -> FunctionModel:
    """Modelo simulado que devolve uma saída estruturada.

    Se o agente aceita mais de um tipo de saída, `tipo` escolhe qual (parte do nome da classe).
    """

    async def modelo(mensagens, info: AgentInfo) -> ModelResponse:
        CHAMADAS.append(nome)
        if espera:
            await asyncio.sleep(espera)
        ferramentas = info.output_tools
        if tipo is not None:
            escolhidas = [f for f in ferramentas if tipo.lower() in f.name.lower()]
            ferramentas = escolhidas or ferramentas
        return ModelResponse(parts=[ToolCallPart(ferramentas[0].name, _valor(dados, mensagens))])

    return FunctionModel(modelo)


def chamar_ferramentas(chamadas, nome: str = "modelo") -> FunctionModel:
    """Modelo simulado que pede ferramentas na primeira vez e responde com texto na segunda.

    `chamadas` é uma lista de (nome_da_ferramenta, argumentos); `final` é montado a partir dos retornos.
    """

    async def modelo(mensagens, info: AgentInfo) -> ModelResponse:
        CHAMADAS.append(nome)
        retornos = [
            parte.content
            for mensagem in mensagens
            for parte in mensagem.parts
            if parte.part_kind == "tool-return"
        ]
        if not retornos:
            return ModelResponse(parts=[ToolCallPart(n, a) for n, a in chamadas])
        return ModelResponse(parts=[TextPart(" | ".join(str(r) for r in retornos))])

    return FunctionModel(modelo)
