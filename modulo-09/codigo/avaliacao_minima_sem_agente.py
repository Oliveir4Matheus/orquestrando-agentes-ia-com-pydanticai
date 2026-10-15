from dataclasses import dataclass

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext


def tarefa(pergunta: str) -> str:
    return "Prazo de devolução: 7 dias."


@dataclass
class MostraContexto(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        print(ctx.name, "|", ctx.inputs, "|", ctx.expected_output, "|", ctx.output)
        return True


conjunto = Dataset(
    name="minimo",
    cases=[Case(name="devolução", inputs="Qual o prazo?", expected_output="7 dias")],
    evaluators=[MostraContexto()],
)

relatorio = conjunto.evaluate_sync(tarefa, progress=False)
print(type(relatorio.cases[0]).__name__, relatorio.cases[0].name)
