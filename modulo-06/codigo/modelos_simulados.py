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


def saida(dados, nome: str = "modelo", espera: float = 0.0) -> FunctionModel:
    """Modelo simulado que devolve uma saída estruturada (para agentes com `output_type`)."""

    async def modelo(mensagens, info: AgentInfo) -> ModelResponse:
        CHAMADAS.append(nome)
        if espera:
            await asyncio.sleep(espera)
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, _valor(dados, mensagens))])

    return FunctionModel(modelo)
