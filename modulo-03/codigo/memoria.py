import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from pydantic_ai import Agent, ModelMessage, ModelMessagesTypeAdapter, RunContext

from config import MODELO


class Fato(BaseModel):
    chave: str
    valor: str


class Fatos(BaseModel):
    fatos: list[Fato]


class Memoria:
    def __init__(self, pasta: Path):
        self.pasta = pasta
        pasta.mkdir(parents=True, exist_ok=True)

    # Curto prazo: eventos crus de uma sessão.
    def salvar_sessao(self, sessao_id: str, mensagens: list[ModelMessage]) -> None:
        (self.pasta / f"sessao_{sessao_id}.json").write_bytes(
            ModelMessagesTypeAdapter.dump_json(mensagens)
        )

    def carregar_sessao(self, sessao_id: str) -> list[ModelMessage]:
        arquivo = self.pasta / f"sessao_{sessao_id}.json"
        if not arquivo.exists():
            return []
        return ModelMessagesTypeAdapter.validate_json(arquivo.read_bytes())

    # Longo prazo: fatos consolidados sobre o cliente.
    def fatos(self, cliente: str) -> dict[str, str]:
        arquivo = self.pasta / f"fatos_{cliente}.json"
        return json.loads(arquivo.read_text()) if arquivo.exists() else {}

    def consolidar(self, cliente: str, novos: list[Fato]) -> list[str]:
        atuais = self.fatos(cliente)
        mudancas = []
        for fato in novos:
            if fato.chave not in atuais:
                mudancas.append(f"novo: {fato.chave} = {fato.valor}")
            elif atuais[fato.chave] != fato.valor:
                mudancas.append(f"atualizado: {fato.chave} = {fato.valor} (antes: {atuais[fato.chave]})")
            atuais[fato.chave] = fato.valor
        (self.pasta / f"fatos_{cliente}.json").write_text(json.dumps(atuais, ensure_ascii=False))
        return mudancas

    def recuperar(self, cliente: str, consulta: str, k: int = 3) -> list[str]:
        palavras = set(re.findall(r"\w+", consulta.lower()))
        pontuados = []
        for chave, valor in self.fatos(cliente).items():
            texto = set(re.findall(r"\w+", f"{chave.replace('_', ' ')} {valor}".lower()))
            pontos = len(palavras & texto)
            if pontos:
                pontuados.append((pontos, f"{chave}: {valor}"))
        return [fato for _, fato in sorted(pontuados, reverse=True)[:k]]


@dataclass
class Contexto:
    memoria: Memoria
    cliente: str


extrator = Agent(
    MODELO,
    output_type=Fatos,
    instructions=(
        "Leia a conversa de atendimento e extraia fatos duráveis sobre o cliente: "
        "preferências, restrições e informações de entrega. Ignore dados de pedidos, "
        "que o sistema já guarda. Use chaves curtas em snake_case e estáveis, como "
        "periodo_entrega_preferido. Devolva uma lista vazia se não houver nada."
    ),
)

atendente = Agent(
    MODELO,
    deps_type=Contexto,
    instructions=(
        "Você atende clientes da loja Casa Verde. Antes de combinar entrega ou "
        "recomendar algo, use `lembrar` para consultar as preferências do cliente. "
        "Responda em até duas frases."
    ),
)


@atendente.tool
def lembrar(ctx: RunContext[Contexto], tema: str) -> str:
    """Consulta a memória de longo prazo sobre o cliente. Use palavras-chave do tema."""
    achados = ctx.deps.memoria.recuperar(ctx.deps.cliente, tema)
    return "\n".join(achados) if achados else "Nada registrado sobre esse tema."


def transcrever(mensagens: list[ModelMessage]) -> str:
    linhas = []
    for mensagem in mensagens:
        for parte in mensagem.parts:
            conteudo = getattr(parte, "content", None)
            if isinstance(conteudo, str) and parte.part_kind in ("user-prompt", "text"):
                papel = "Cliente" if parte.part_kind == "user-prompt" else "Atendente"
                linhas.append(f"{papel}: {conteudo}")
    return "\n".join(linhas)


def encerrar_sessao(memoria: Memoria, cliente: str, sessao_id: str, mensagens: list[ModelMessage]) -> list[str]:
    memoria.salvar_sessao(sessao_id, mensagens)
    novos = extrator.run_sync(transcrever(mensagens)).output.fatos
    return memoria.consolidar(cliente, novos)
