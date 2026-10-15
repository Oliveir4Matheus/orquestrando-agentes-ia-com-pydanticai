from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import MaxToolCalls

from atendente import atendente
from avaliadores import ContemEsperado
from comportamento_simulado import roteirizado


async def tarefa(pergunta: str) -> str:
    resultado = await atendente.run(pergunta, model=roteirizado())
    return resultado.output


CASOS = [
    Case(name="status enviado", inputs="Onde está o pedido 1001?", expected_output="enviado"),
    Case(name="status em separação", inputs="Onde está o pedido 1002?", expected_output="separação"),
    Case(name="prazo de devolução", inputs="Qual é o prazo de devolução?", expected_output="7 dias"),
    Case(name="frete grátis", inputs="O frete é grátis acima de quanto?", expected_output="200"),
    Case(name="cancelar em separação", inputs="Posso cancelar o pedido 1002?", expected_output="pode ser cancelado"),
    Case(name="cancelar já enviado", inputs="Posso cancelar o pedido 1001?", expected_output="não"),
    Case(name="fora do assunto", inputs="Qual é a capital da França?", expected_output="não posso"),
    Case(name="pergunta composta", inputs="Compare os pedidos 1001 e 1002.", expected_output="separação"),
]


def conjunto() -> Dataset:
    return Dataset(
        name="atendimento-casa-verde",
        cases=CASOS,
        evaluators=[ContemEsperado(), MaxToolCalls(max_calls=3)],
    )
