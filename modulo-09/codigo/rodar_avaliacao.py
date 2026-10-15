from avaliacao import conjunto, tarefa


def resumir(relatorio) -> None:
    for caso in relatorio.cases:
        marcas = " ".join(
            f"{nome}:{'ok' if resultado.value else 'FALHA'}"
            for nome, resultado in caso.assertions.items()
        )
        print(f"{caso.name:24s} {marcas}")
    aprovados = sum(all(r.value for r in c.assertions.values()) for c in relatorio.cases)
    print(f"\nAprovados: {aprovados} de {len(relatorio.cases)}")


if __name__ == "__main__":
    resumir(conjunto().evaluate_sync(tarefa, progress=False))
