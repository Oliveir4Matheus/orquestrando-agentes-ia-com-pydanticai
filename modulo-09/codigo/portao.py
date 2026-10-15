from pydantic_evals import Dataset

from avaliacao import CASOS, tarefa
from avaliadores import ContemEsperado

REGRESSAO = {"status enviado", "status em separação", "prazo de devolução", "frete grátis", "cancelar em separação"}


def dividir() -> tuple[Dataset, Dataset]:
    regressao = [c for c in CASOS if c.name in REGRESSAO]
    capacidade = [c for c in CASOS if c.name not in REGRESSAO]
    return (
        Dataset(name="regressao", cases=regressao, evaluators=[ContemEsperado()]),
        Dataset(name="capacidade", cases=capacidade, evaluators=[ContemEsperado()]),
    )


def taxa(relatorio) -> float:
    aprovados = sum(all(r.value for r in c.assertions.values()) for c in relatorio.cases)
    return aprovados / len(relatorio.cases)


def saturada(historico: list[float], limite: float = 0.98, execucoes: int = 3) -> bool:
    return len(historico) >= execucoes and all(t >= limite for t in historico[-execucoes:])


if __name__ == "__main__":
    regressao, capacidade = dividir()
    t_regressao = taxa(regressao.evaluate_sync(tarefa, progress=False))
    t_capacidade = taxa(capacidade.evaluate_sync(tarefa, progress=False))

    print(f"Regressão : {t_regressao:.0%} (exigido: 100%) -> {'APROVADO' if t_regressao == 1.0 else 'REPROVADO: bloqueie a mudança'}")
    print(f"Capacidade: {t_capacidade:.0%} (meta: crescer) -> acompanhar; não bloqueia")
    print()
    print("Saturada com [0.97, 1.0, 1.0, 1.0]?", saturada([0.97, 1.0, 1.0, 1.0]))
    print("Saturada com [1.0, 0.9, 1.0, 1.0]?", saturada([1.0, 0.9, 1.0, 1.0]))
