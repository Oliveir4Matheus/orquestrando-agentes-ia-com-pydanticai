from pydantic_ai import Agent

from busca import indice
from config import MODELO_RAPIDO

LIMIAR = 0.2

reformulador = Agent(
    MODELO_RAPIDO,
    name="reformulador",
    instructions=(
        "A busca na base de políticas não achou nada relevante. Reescreva a consulta "
        "com o vocabulário da loja (devolução, reembolso, cancelamento, frete, "
        "pagamento, troca). Responda apenas com a nova consulta."
    ),
)


async def buscar_com_laco(consulta: str, max_voltas: int = 3):
    tentativas = []
    for volta in range(1, max_voltas + 1):
        pontos, fragmento = indice.buscar(consulta, k=1)[0]
        tentativas.append((consulta, round(pontos, 2)))
        if pontos >= LIMIAR:
            return fragmento, tentativas
        if volta < max_voltas:
            consulta = (await reformulador.run(f"Consulta anterior: {consulta}")).output
    return None, tentativas
