import random


def pass_at_k(p: float, k: int) -> float:
    """Probabilidade de pelo menos um sucesso em k tentativas."""
    return 1 - (1 - p) ** k


def pass_hat_k(p: float, k: int) -> float:
    """Probabilidade de todas as k tentativas darem certo."""
    return p**k


def simular(p: float, tarefas: int, k: int, semente: int = 7) -> tuple[float, float]:
    sorteio = random.Random(semente)
    pelo_menos_uma = todas = 0
    for _ in range(tarefas):
        tentativas = [sorteio.random() < p for _ in range(k)]
        pelo_menos_uma += any(tentativas)
        todas += all(tentativas)
    return pelo_menos_uma / tarefas, todas / tarefas


P = 0.75
print(f"Taxa de acerto por tentativa: {P:.0%}\n")
print(" k   pass@k   pass^k   (simulado: pass@k / pass^k, 2000 tarefas)")
for k in (1, 3, 5, 10):
    empirico_a, empirico_t = simular(P, 2000, k)
    print(f"{k:2d}   {pass_at_k(P, k):6.3f}   {pass_hat_k(P, k):6.3f}   ({empirico_a:.3f} / {empirico_t:.3f})")
