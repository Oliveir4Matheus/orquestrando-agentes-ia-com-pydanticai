import asyncio
import time
from typing import Literal

from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO_RAPIDO


class Sentimento(BaseModel):
    valor: Literal["positivo", "neutro", "negativo"]


class Categoria(BaseModel):
    valor: Literal["entrega", "produto", "pagamento", "outro"]


class DadosPessoais(BaseModel):
    contem: bool


agente_sentimento = Agent(MODELO_RAPIDO, output_type=Sentimento,
                          instructions="Classifique o sentimento da mensagem do cliente.")
agente_categoria = Agent(MODELO_RAPIDO, output_type=Categoria,
                         instructions="Classifique o assunto da mensagem do cliente.")
agente_pii = Agent(MODELO_RAPIDO, output_type=DadosPessoais,
                   instructions="Diga se a mensagem contém dado pessoal, como CPF, telefone ou e-mail.")


async def analisar(mensagem: str) -> dict:
    sentimento, categoria, pii = await asyncio.gather(
        agente_sentimento.run(mensagem),
        agente_categoria.run(mensagem),
        agente_pii.run(mensagem),
    )
    return {
        "sentimento": sentimento.output.valor,
        "categoria": categoria.output.valor,
        "dados_pessoais": pii.output.contem,
    }


async def analisar_em_sequencia(mensagem: str) -> dict:
    sentimento = await agente_sentimento.run(mensagem)
    categoria = await agente_categoria.run(mensagem)
    pii = await agente_pii.run(mensagem)
    return {
        "sentimento": sentimento.output.valor,
        "categoria": categoria.output.valor,
        "dados_pessoais": pii.output.contem,
    }


async def cronometrar(funcao, mensagem: str):
    inicio = time.perf_counter()
    resultado = await funcao(mensagem)
    return resultado, time.perf_counter() - inicio
