from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

import instrumentacao  # noqa: F401

RUBRICA = (
    "A resposta reconhece o problema do cliente com empatia, informa um próximo "
    "passo concreto e não promete reembolso nem prazo que a loja não confirmou."
)

RESPOSTAS = {
    "boa 1": "Sinto muito pelo vaso quebrado. Vou abrir uma troca agora e nossa equipe retorna por e-mail.",
    "boa 2": "Lamento o atraso. Já estou verificando o pedido 1001 com a transportadora e aviso você hoje.",
    "seca": "Pedido registrado.",
    "promete": "Pode ficar tranquila: reembolso garantido em 24 horas.",
    "promete com empatia": "Sinto muito! Garantimos seu reembolso em 24 horas.",
}


def juiz_simulado(mensagens, info):
    """Um juiz fictício: exige empatia e proíbe promessas. Devolve o veredito no formato do LLMJudge."""
    texto = str(mensagens[-1].parts[-1].content).lower()
    empatico = "sinto" in texto or "lamento" in texto
    promete = "garant" in texto
    aprovado = empatico and not promete
    motivo = (
        "reconhece o problema e não promete" if aprovado
        else "promete algo não confirmado" if promete
        else "não demonstra empatia nem próximo passo"
    )
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
        "reason": motivo, "pass": aprovado, "score": 1.0 if aprovado else 0.0,
    })])


async def tarefa(chave: str) -> str:
    return RESPOSTAS[chave]


def conjunto() -> Dataset:
    return Dataset(
        name="juiz-de-tom",
        cases=[Case(name=chave, inputs=chave) for chave in RESPOSTAS],
        evaluators=[LLMJudge(rubric=RUBRICA, model=FunctionModel(juiz_simulado), assertion={"evaluation_name": "tom_adequado", "include_reason": True})],
    )


if __name__ == "__main__":
    relatorio = conjunto().evaluate_sync(tarefa, progress=False)
    for c in relatorio.cases:
        veredito = c.assertions["tom_adequado"]
        print(f"{c.name:22s} {'aprovada' if veredito.value else 'reprovada':10s} {veredito.reason}")
