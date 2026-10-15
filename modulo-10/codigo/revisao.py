import random

from pydantic_evals import Case

from producao import Registro, gerar_registros


def amostra_para_revisao(registros: list[Registro], fracao: float = 0.02, semente: int = 7) -> list[Registro]:
    """Todos os casos suspeitos mais uma amostra aleatória dos demais."""
    suspeitos = [
        r for r in registros
        if r.escalou_para_humano or r.guardrail_acionado or r.dado_pessoal_na_saida
    ]
    ids_suspeitos = {r.id for r in suspeitos}
    restantes = [r for r in registros if r.id not in ids_suspeitos]
    sorteio = random.Random(semente)
    aleatorios = sorteio.sample(restantes, k=int(len(restantes) * fracao))
    return suspeitos + aleatorios


def virar_caso(registro: Registro, conversa: str, esperado: str) -> Case:
    """Uma falha confirmada por uma pessoa vira uma tarefa do conjunto de avaliação."""
    return Case(name=f"produção {registro.id}", inputs=conversa, expected_output=esperado)


if __name__ == "__main__":
    registros = gerar_registros(1000, semente=2, taxa_de_resolucao=0.78)
    fila = amostra_para_revisao(registros)
    falhas = [r for r in registros if r.resolveu is False]
    print(f"Atendimentos: {len(registros)}")
    print(f"Casos na fila de revisão (suspeitos e amostra): {len(fila)}")
    print(f"Fila como fração do total: {len(fila) / len(registros):.0%}")

    caso = virar_caso(falhas[0], "Posso cancelar o pedido 1001?", "não")
    print("\nNovo caso do conjunto:", caso.name, "|", caso.inputs, "->", caso.expected_output)
