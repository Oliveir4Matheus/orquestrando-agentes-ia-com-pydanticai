from dataclasses import dataclass

from pydantic_evals.evaluators import Evaluator, EvaluatorContext


@dataclass
class ContemEsperado(Evaluator):
    """Aprova se a resposta contém o trecho esperado do caso, sem diferenciar maiúsculas."""

    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.expected_output.lower() in ctx.output.lower()
