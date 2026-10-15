from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido


class Reclamacao(BaseModel):
    codigo_pedido: str | None
    problema: str
    urgencia: Literal["baixa", "media", "alta"]


extrator = Agent(
    MODELO,
    output_type=Reclamacao,
    instructions=(
        "Extraia da mensagem do cliente o código do pedido (4 dígitos, ou null se "
        "não houver), o problema relatado e a urgência."
    ),
)

redator = Agent(
    MODELO,
    instructions=(
        "Escreva uma resposta cordial de até três frases a uma reclamação, "
        "usando apenas os dados fornecidos. Termine com 'Equipe Casa Verde'."
    ),
)


def atender(mensagem: str) -> str:
    reclamacao = extrator.run_sync(mensagem).output

    if reclamacao.codigo_pedido is None:  # porta de verificação 1
        return "Para ajudar, preciso do código do pedido. Pode me informar? Equipe Casa Verde"

    pedido = buscar_pedido(reclamacao.codigo_pedido)
    if pedido is None:  # porta de verificação 2
        return f"Não encontrei o pedido {reclamacao.codigo_pedido}. Pode conferir o número? Equipe Casa Verde"

    return redator.run_sync(
        f"Reclamação: {reclamacao.problema}\n"
        f"Urgência: {reclamacao.urgencia}\n"
        f"Dados do pedido: {pedido}"
    ).output
