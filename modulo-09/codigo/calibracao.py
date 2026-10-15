# Veredito de uma pessoa especialista e do juiz automático sobre as mesmas 10 respostas.
HUMANO = [True, True, False, False, True, False, True, True, False, True]
JUIZ   = [True, True, False, True,  True, False, True, False, False, True]


def calibrar(humano: list[bool], juiz: list[bool]) -> dict:
    n = len(humano)
    concordancias = sum(h == j for h, j in zip(humano, juiz))
    brando = sum(j and not h for h, j in zip(humano, juiz))  # juiz aprova o que a pessoa reprovou
    duro = sum(h and not j for h, j in zip(humano, juiz))  # juiz reprova o que a pessoa aprovou
    p_observado = concordancias / n
    p_humano, p_juiz = sum(humano) / n, sum(juiz) / n
    p_acaso = p_humano * p_juiz + (1 - p_humano) * (1 - p_juiz)
    kappa = (p_observado - p_acaso) / (1 - p_acaso)
    return {"concordancia": p_observado, "brando": brando, "duro": duro, "kappa": kappa}


resultado = calibrar(HUMANO, JUIZ)
print(f"Concordância com a pessoa: {resultado['concordancia']:.0%}")
print(f"Juiz brando demais (aprovou o que a pessoa reprovou): {resultado['brando']}")
print(f"Juiz duro demais (reprovou o que a pessoa aprovou): {resultado['duro']}")
print(f"Kappa de Cohen: {resultado['kappa']:.2f}")
