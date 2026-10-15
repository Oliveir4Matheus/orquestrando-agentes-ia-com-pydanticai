from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent, ModelRetry, RunContext, Tool

from config import MODELO

MAX_COLABORADORES = 10


@dataclass
class Colaborador:
    nome: str
    descricao: str  # instruções de colaboração: quando o supervisor deve usar este colaborador
    executar: Callable[[str, list | None], Awaitable[str]]
    repassar_historico: bool = False


def de_agente(nome: str, descricao: str, agente: Agent, repassar_historico: bool = False) -> Colaborador:
    async def executar(pergunta: str, historico: list | None) -> str:
        resposta = await agente.run(pergunta, message_history=historico)
        return resposta.output

    return Colaborador(nome, descricao, executar, repassar_historico)


def de_equipe(nome: str, descricao: str, equipe: "Equipe") -> Colaborador:
    async def executar(pergunta: str, historico: list | None) -> str:
        return await equipe.atender(pergunta, historico)

    return Colaborador(nome, descricao, executar)


class Escolha(BaseModel):
    colaborador: str


class Equipe:
    def __init__(self, colaboradores: list[Colaborador],
                 modo: Literal["coordenar", "rotear"] = "coordenar", modelo=MODELO):
        if len(colaboradores) > MAX_COLABORADORES:
            raise ValueError(f"No máximo {MAX_COLABORADORES} colaboradores por supervisor.")
        if len({c.nome for c in colaboradores}) != len(colaboradores):
            raise ValueError("Os nomes dos colaboradores devem ser únicos.")

        self.modo = modo
        self.por_nome = {c.nome: c for c in colaboradores}
        catalogo = "\n".join(f"- {c.nome}: {c.descricao}" for c in colaboradores)

        if modo == "rotear":
            self.supervisor = Agent(
                modelo,
                name="supervisor",
                output_type=Escolha,
                instructions=f"Escolha o colaborador mais adequado à pergunta.\nColaboradores:\n{catalogo}",
            )

            @self.supervisor.output_validator
            def conferir(escolha: Escolha) -> Escolha:
                if escolha.colaborador not in self.por_nome:
                    raise ModelRetry(f"Colaborador inexistente. Opções: {', '.join(self.por_nome)}.")
                return escolha
        else:
            self.supervisor = Agent(
                modelo,
                name="supervisor",
                deps_type=list,
                tools=[self._ferramenta(c) for c in colaboradores],
                instructions=(
                    "Coordene os colaboradores para responder ao cliente em uma mensagem "
                    f"única e cordial.\nColaboradores:\n{catalogo}"
                ),
            )

    def _ferramenta(self, colaborador: Colaborador) -> Tool:
        async def chamar(ctx: RunContext[list], pergunta: str) -> str:
            historico = ctx.deps if colaborador.repassar_historico else None
            return await colaborador.executar(pergunta, historico)

        return Tool(chamar, name=colaborador.nome, description=colaborador.descricao)

    async def atender(self, pergunta: str, historico: list | None = None) -> str:
        if self.modo == "rotear":
            escolha = (await self.supervisor.run(pergunta, message_history=historico)).output
            colaborador = self.por_nome[escolha.colaborador]
            return await colaborador.executar(pergunta, historico if colaborador.repassar_historico else None)
        resposta = await self.supervisor.run(pergunta, message_history=historico, deps=historico or [])
        return resposta.output
