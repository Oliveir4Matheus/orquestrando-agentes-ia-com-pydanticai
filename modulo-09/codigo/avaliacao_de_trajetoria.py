from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import MaxModelRequests, TrajectoryMatch

from atendente import atendente
from comportamento_simulado import roteirizado


async def tarefa(pergunta: str) -> str:
    return (await atendente.run(pergunta, model=roteirizado())).output


def caso(nome, pergunta, trajetoria):
    return Case(
        name=nome,
        inputs=pergunta,
        evaluators=[TrajectoryMatch(expected_trajectory=trajetoria, order="exact")],
    )


CASOS = [
    caso("status enviado", "Onde está o pedido 1001?", ["consultar_pedido"]),
    caso("prazo de devolução", "Qual é o prazo de devolução?", ["consultar_politica"]),
    caso("cancelar já enviado", "Posso cancelar o pedido 1001?", ["consultar_pedido"]),
    caso("fora do assunto", "Qual é a capital da França?", []),
    caso("pergunta composta", "Compare os pedidos 1001 e 1002.", ["consultar_pedido", "consultar_pedido"]),
]


def conjunto() -> Dataset:
    return Dataset(name="trajetoria", cases=CASOS, evaluators=[MaxModelRequests(max_requests=3)])


if __name__ == "__main__":
    relatorio = conjunto().evaluate_sync(tarefa, progress=False)
    for c in relatorio.cases:
        trajetoria = c.scores["TrajectoryMatch"]
        orcamento = c.assertions["MaxModelRequests"].value
        print(f"{c.name:22s} trajetória={trajetoria.value:.1f}  orçamento={'ok' if orcamento else 'FALHA'}")
