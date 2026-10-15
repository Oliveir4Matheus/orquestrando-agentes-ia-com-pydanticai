from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected


def status_do_pedido(codigo: str) -> str:
    pedidos = {"1001": "enviado", "1002": "em separação"}
    return pedidos.get(codigo, "desconhecido")


casos = Dataset(
    name="status_casa_verde",
    cases=[
        Case(name="pedido_enviado", inputs="1001", expected_output="enviado"),
        Case(name="pedido_entregue", inputs="1003", expected_output="entregue"),
    ],
    evaluators=[EqualsExpected()],
)

relatorio = casos.evaluate_sync(status_do_pedido, progress=False)
for caso in relatorio.cases:
    print(caso.name, "->", caso.output, "| passou:", caso.assertions["EqualsExpected"].value)
