from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

import instrumentacao  # noqa: F401

RUBRICA = "A resposta reconhece o problema do cliente com empatia."
vistos = []


def juiz_espiao(mensagens, info):
    """Guarda o que o juiz recebeu e devolve sempre um veredito aprovado."""
    vistos.append(str(mensagens[-1].parts[-1].content))
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
        "reason": "ok", "pass": True, "score": 0.8,
    })])


async def tarefa(pergunta: str) -> str:
    return "Sinto muito pelo transtorno."


modelo = FunctionModel(juiz_espiao)
conjunto = Dataset(
    name="juiz-configuracao",
    cases=[Case(name="vaso", inputs="Meu vaso chegou quebrado.")],
    evaluators=[
        LLMJudge(rubric=RUBRICA, model=modelo),
        LLMJudge(
            rubric=RUBRICA, model=modelo, include_input=True,
            assertion={"evaluation_name": "tom_adequado"}, score={"evaluation_name": "nota_de_tom"},
        ),
    ],
)
relatorio = conjunto.evaluate_sync(tarefa, progress=False)
caso = relatorio.cases[0]
print("Asserções:", sorted(caso.assertions))
print("Notas:", {nome: r.value for nome, r in caso.scores.items()})
print("Envios ao juiz com a mensagem do cliente:", sum("quebrado" in v for v in vistos), "de", len(vistos))
