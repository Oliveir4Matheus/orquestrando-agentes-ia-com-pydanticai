from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO


class Resposta(BaseModel):
    texto: str


class Transferencia(BaseModel):
    destino: Literal["pedidos", "reclamacoes", "politicas"]
    motivo: str


triagem = Agent(
    MODELO,
    name="triagem",
    output_type=Transferencia,
    instructions=(
        "Você é a triagem do atendimento da Casa Verde. Transfira o cliente para "
        "`pedidos` (status e rastreio), `politicas` (regras da loja) ou "
        "`reclamacoes` (insatisfação ou defeito). Não responda ao cliente."
    ),
)

pedidos = Agent(
    MODELO,
    name="pedidos",
    output_type=Resposta | Transferencia,
    instructions=(
        "Você responde sobre status de pedidos. Se o cliente estiver insatisfeito, "
        "transfira para `reclamacoes`; se a pergunta for sobre regras da loja, "
        "transfira para `politicas`."
    ),
)

politicas = Agent(
    MODELO,
    name="politicas",
    output_type=Resposta | Transferencia,
    instructions="Você responde sobre regras da loja. Se a pergunta for sobre um pedido, transfira para `pedidos`.",
)

reclamacoes = Agent(
    MODELO,
    name="reclamacoes",
    output_type=Resposta | Transferencia,
    instructions="Você acolhe reclamações com empatia e explica o próximo passo. Não prometa reembolso.",
)

AGENTES = {"triagem": triagem, "pedidos": pedidos, "politicas": politicas, "reclamacoes": reclamacoes}

FALLBACK = "Não consegui concluir o atendimento por aqui. Vou chamar um atendente."


async def atender(mensagem: str, max_transferencias: int = 3) -> tuple[str, list[str]]:
    atual, historico, prompt = "triagem", None, mensagem
    trilha = [atual]
    for _ in range(max_transferencias + 1):
        resultado = await AGENTES[atual].run(prompt, message_history=historico)
        if isinstance(resultado.output, Resposta):
            return resultado.output.texto, trilha
        historico = resultado.all_messages()
        atual = resultado.output.destino
        trilha.append(atual)
        prompt = f"Atendimento transferido ({resultado.output.motivo}). Continue de onde parou."
    return FALLBACK, trilha
