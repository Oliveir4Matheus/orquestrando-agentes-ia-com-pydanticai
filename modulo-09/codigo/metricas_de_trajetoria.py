from collections import Counter


def exata(real: list[str], esperada: list[str]) -> float:
    return 1.0 if real == esperada else 0.0


def f1(precisao: float, revocacao: float) -> float:
    return 0.0 if precisao + revocacao == 0 else 2 * precisao * revocacao / (precisao + revocacao)


def _maior_subsequencia(a: list[str], b: list[str]) -> int:
    tabela = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, start=1):
        for j, y in enumerate(b, start=1):
            tabela[i][j] = tabela[i - 1][j - 1] + 1 if x == y else max(tabela[i - 1][j], tabela[i][j - 1])
    return tabela[-1][-1]


def na_ordem(real: list[str], esperada: list[str]) -> float:
    """F1 sobre a maior subsequência comum: chamadas extras custam precisão; faltantes, revocação."""
    comum = _maior_subsequencia(real, esperada)
    if not real and not esperada:
        return 1.0
    precisao = comum / len(real) if real else 0.0
    revocacao = comum / len(esperada) if esperada else 0.0
    return f1(precisao, revocacao)


def em_qualquer_ordem(real: list[str], esperada: list[str]) -> float:
    comum = sum((Counter(real) & Counter(esperada)).values())
    if not real and not esperada:
        return 1.0
    precisao = comum / len(real) if real else 0.0
    revocacao = comum / len(esperada) if esperada else 0.0
    return f1(precisao, revocacao)


def precisao(real: list[str], esperada: list[str]) -> float:
    comum = sum((Counter(real) & Counter(esperada)).values())
    return comum / len(real) if real else 1.0


def revocacao(real: list[str], esperada: list[str]) -> float:
    comum = sum((Counter(real) & Counter(esperada)).values())
    return comum / len(esperada) if esperada else 1.0


def usou_a_ferramenta(real: list[str], ferramenta: str) -> bool:
    return ferramenta in real
