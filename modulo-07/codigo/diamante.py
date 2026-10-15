from pydantic_ai import Agent

from config import MODELO, MODELO_RAPIDO

especialista = Agent(
    MODELO,
    name="especialista",
    instructions="Responda com precisão e sem enfeites, em até duas frases.",
)

reescritor = Agent(
    MODELO_RAPIDO,
    name="reescritor",
    instructions=(
        "Reescreva a resposta no tom da marca Casa Verde: acolhedor, direto, sem "
        "jargão. Preserve todos os fatos, números e prazos. Não acrescente informação."
    ),
)


async def responder(pergunta: str) -> tuple[str, str]:
    bruta = (await especialista.run(pergunta)).output
    final = (await reescritor.run(f"Pergunta: {pergunta}\nResposta: {bruta}")).output
    return bruta, final
