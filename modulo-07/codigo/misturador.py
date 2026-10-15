import asyncio

from pydantic import BaseModel, Field

from pydantic_ai import Agent

from config import MODELO


class Parecer(BaseModel):
    texto: str
    confianca: float = Field(ge=0, le=1)


def especialista(nome: str, foco: str) -> Agent:
    return Agent(
        MODELO,
        name=nome,
        output_type=Parecer,
        instructions=f"Responda apenas sobre {foco}. Informe sua confiança de 0 a 1.",
    )


agente_pedidos = especialista("pedidos", "o status do pedido do cliente")
agente_politicas = especialista("politicas", "as regras de devolução da loja")
agente_conteudo = especialista("cuidados", "o cuidado e a limpeza do produto")

misturador = Agent(
    MODELO,
    name="misturador",
    instructions=(
        "Você recebe pareceres de especialistas, cada um com uma confiança. Junte as "
        "partes úteis em uma única resposta curta. Descarte o que for irrelevante ou "
        "contraditório e não acrescente nada que não esteja nos pareceres."
    ),
)


async def responder(pergunta: str) -> str:
    pareceres = await asyncio.gather(*(
        a.run(pergunta) for a in (agente_pedidos, agente_politicas, agente_conteudo)
    ))
    texto = "\n".join(
        f"[{a.name} | confiança {p.output.confianca:.2f}] {p.output.texto}"
        for a, p in zip((agente_pedidos, agente_politicas, agente_conteudo), pareceres)
    )
    return (await misturador.run(f"Pergunta: {pergunta}\nPareceres:\n{texto}")).output
