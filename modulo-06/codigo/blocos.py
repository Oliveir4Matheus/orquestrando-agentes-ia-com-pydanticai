import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic_ai import Agent

Estado = dict[str, Any]
Etapa = Callable[[Estado], Awaitable[None]]

REGISTRO: list[str] = []


def agente(nome: str, ag: Agent, entrada: Callable[[Estado], str], saida: str) -> Etapa:
    """Etapa que chama um agente e guarda a saída no estado."""

    async def etapa(estado: Estado) -> None:
        REGISTRO.append(nome)
        resultado = await ag.run(entrada(estado))
        estado[saida] = resultado.output

    return etapa


def codigo(nome: str, funcao: Callable[[Estado], Any], saida: str) -> Etapa:
    """Etapa determinística: roda uma função comum e guarda o resultado no estado."""

    async def etapa(estado: Estado) -> None:
        REGISTRO.append(nome)
        estado[saida] = funcao(estado)

    return etapa


def sequencial(*etapas: Etapa) -> Etapa:
    async def etapa(estado: Estado) -> None:
        for passo in etapas:
            await passo(estado)

    return etapa


def paralelo(*etapas: Etapa) -> Etapa:
    async def etapa(estado: Estado) -> None:
        await asyncio.gather(*(passo(estado) for passo in etapas))

    return etapa


def repetir(*etapas: Etapa, maximo: int, parar: Callable[[Estado], bool]) -> Etapa:
    async def etapa(estado: Estado) -> None:
        for _ in range(maximo):
            for passo in etapas:
                await passo(estado)
                if parar(estado):
                    return

    return etapa


def rotear(escolher: Callable[[Estado], Awaitable[str]], rotas: dict[str, Etapa]) -> Etapa:
    async def etapa(estado: Estado) -> None:
        chave = await escolher(estado)
        REGISTRO.append(f"rota:{chave}")
        await rotas[chave](estado)

    return etapa
