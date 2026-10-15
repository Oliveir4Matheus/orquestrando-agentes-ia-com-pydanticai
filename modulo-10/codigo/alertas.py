LIMITES = {
    "qualidade: taxa de resolução": ("minimo", 0.80),
    "desempenho: latência p95 (s)": ("maximo", 3.5),
    "responsabilidade: dado pessoal na saída": ("maximo", 0.005),
    "custo: R$ por atendimento": ("maximo", 0.05),
}


def conferir(metricas: dict[str, float]) -> list[str]:
    avisos = []
    for nome, (tipo, limite) in LIMITES.items():
        valor = metricas[nome]
        if (tipo == "minimo" and valor < limite) or (tipo == "maximo" and valor > limite):
            avisos.append(f"ALERTA {nome}: {valor:.3f} ({'abaixo' if tipo == 'minimo' else 'acima'} de {limite})")
    return avisos
