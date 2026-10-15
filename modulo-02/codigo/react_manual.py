import asyncio
import re

from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido, buscar_politica

INSTRUCOES = """\
Resolva a tarefa alternando passos. Em cada resposta, escreva exatamente:

Pensamento: <o que você pretende fazer e por quê>
Ação: <ferramenta>[<argumento>]

e pare. As ferramentas são:
- pedido[codigo]: devolve os dados de um pedido;
- politica[tema]: devolve uma política da loja (devolucao, cancelamento, frete).

Quando souber a resposta, escreva:

Pensamento: <resumo do que descobriu>
Resposta final: <resposta ao cliente>

Nunca escreva "Observação:"; ela será fornecida a você.
"""

raciocinador = Agent(MODELO, instructions=INSTRUCOES)

FERRAMENTAS = {
    "pedido": lambda argumento: str(buscar_pedido(argumento)),
    "politica": lambda argumento: str(asyncio.run(buscar_politica(argumento))),
}


def reagir(tarefa: str, max_passos: int = 6) -> str:
    texto = f"Tarefa: {tarefa}\n"
    for _ in range(max_passos):
        passo = raciocinador.run_sync(texto).output
        passo = passo.split("Observação:")[0].strip()
        print(passo)
        texto += passo + "\n"

        if "Resposta final:" in passo:
            return passo.split("Resposta final:")[1].strip()

        achado = re.search(r"Ação:\s*(\w+)\[(.*?)\]", passo)
        if achado is None:
            return "Não consegui decidir o próximo passo."

        nome, argumento = achado.groups()
        if nome in FERRAMENTAS:
            observacao = FERRAMENTAS[nome](argumento)
        else:
            observacao = f"A ferramenta {nome} não existe."
        print(f"Observação: {observacao}")
        texto += f"Observação: {observacao}\n"
    return "Limite de passos atingido."


if __name__ == "__main__":
    reagir("Meu pedido 1003 chegou com defeito. Ainda consigo devolver?")
