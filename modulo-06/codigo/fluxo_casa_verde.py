import re
from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent

from blocos import agente, codigo, paralelo, repetir, rotear, sequencial
from busca import indice
from config import MODELO, MODELO_RAPIDO
from loja import buscar_pedido


class Rota(BaseModel):
    categoria: Literal["reclamacao", "outro"]


class Avaliacao(BaseModel):
    problemas: list[str]
    aprovado: bool


classificador = Agent(MODELO_RAPIDO, output_type=Rota, instructions="Classifique a mensagem do cliente.")
redator = Agent(MODELO, instructions="Responda à reclamação com empatia, em até quatro frases.")
avaliador = Agent(MODELO, output_type=Avaliacao, instructions="Avalie a resposta e liste os problemas.")
generalista = Agent(MODELO, instructions="Responda com cordialidade e encaminhe a um atendente.")


async def escolher_rota(estado) -> str:
    resultado = await classificador.run(estado["mensagem"])
    return resultado.output.categoria


def buscar_dados_do_pedido(estado):
    achado = re.search(r"\d{4}", estado["mensagem"])
    return buscar_pedido(achado.group()) if achado else None


def buscar_politica_relevante(estado):
    pontos, fragmento = indice.buscar(estado["mensagem"], k=1)[0]
    return fragmento.texto if pontos >= 0.2 else None


def prompt_do_redator(estado):
    texto = f"Reclamação: {estado['mensagem']}\nPedido: {estado['pedido']}\nPolítica: {estado['politica']}"
    if estado.get("avaliacao") and not estado["avaliacao"].aprovado:
        problemas = "; ".join(estado["avaliacao"].problemas)
        texto += f"\nResposta anterior: {estado['resposta']}\nCorrija: {problemas}"
    return texto


fluxo_reclamacao = sequencial(
    paralelo(
        codigo("buscar_pedido", buscar_dados_do_pedido, "pedido"),
        codigo("buscar_politica", buscar_politica_relevante, "politica"),
    ),
    agente("redigir", redator, prompt_do_redator, "resposta"),
    repetir(
        agente("avaliar", avaliador, lambda e: f"Resposta: {e['resposta']}", "avaliacao"),
        agente("revisar", redator, prompt_do_redator, "resposta"),
        maximo=2,
        parar=lambda e: e["avaliacao"].aprovado,
    ),
)

fluxo = rotear(escolher_rota, {
    "reclamacao": fluxo_reclamacao,
    "outro": agente("generalista", generalista, lambda e: e["mensagem"], "resposta"),
})
