from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO, MODELO_RAPIDO
from rag import agente_rag

Categoria = Literal["pedido", "politica", "reclamacao", "outro"]


class Rota(BaseModel):
    categoria: Categoria


classificador = Agent(
    MODELO_RAPIDO,
    output_type=Rota,
    instructions=(
        "Classifique a mensagem do cliente: `pedido` (status ou rastreio de um "
        "pedido), `politica` (regras de devolução, troca, frete ou pagamento), "
        "`reclamacao` (insatisfação ou defeito) ou `outro`."
    ),
)

agente_pedidos = Agent(
    MODELO,
    instructions="Você informa o status de pedidos da Casa Verde com base nos dados fornecidos.",
)

agente_reclamacoes = Agent(
    MODELO,
    instructions=(
        "Você acolhe reclamações com empatia, pede desculpas uma vez e explica o "
        "próximo passo. Não prometa reembolso."
    ),
)

agente_geral = Agent(
    MODELO,
    instructions="Você responde com cordialidade e encaminha para um atendente humano.",
)

ESPECIALISTAS = {
    "pedido": agente_pedidos,
    "politica": agente_rag,
    "reclamacao": agente_reclamacoes,
    "outro": agente_geral,
}


def atender(mensagem: str) -> tuple[str, str]:
    categoria = classificador.run_sync(mensagem).output.categoria
    resposta = ESPECIALISTAS[categoria].run_sync(mensagem).output
    return categoria, resposta
