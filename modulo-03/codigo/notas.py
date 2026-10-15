import json
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext

from config import MODELO


@dataclass
class Caderno:
    arquivo: Path

    def ler(self) -> list[str]:
        if not self.arquivo.exists():
            return []
        return json.loads(self.arquivo.read_text())

    def anotar(self, texto: str) -> None:
        notas = self.ler() + [texto]
        self.arquivo.write_text(json.dumps(notas, ensure_ascii=False))


agente = Agent(
    MODELO,
    deps_type=Caderno,
    instructions=(
        "Você atende clientes da loja Casa Verde. Use `anotar` para registrar "
        "decisões, promessas e preferências do cliente que precisem ser "
        "lembradas em atendimentos futuros. Responda em até duas frases."
    ),
)


@agente.instructions
def notas_anteriores(ctx: RunContext[Caderno]) -> str:
    notas = ctx.deps.ler()
    if not notas:
        return ""
    return "Notas de atendimentos anteriores:\n" + "\n".join(f"- {nota}" for nota in notas)


@agente.tool
def anotar(ctx: RunContext[Caderno], texto: str) -> str:
    """Guarda uma nota curta para ser lembrada em atendimentos futuros."""
    ctx.deps.anotar(texto)
    return "Nota registrada."
