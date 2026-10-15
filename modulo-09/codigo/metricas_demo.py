from metricas_de_trajetoria import (
    em_qualquer_ordem, exata, na_ordem, precisao, revocacao, usou_a_ferramenta,
)

ESPERADA = ["consultar_pedido", "consultar_politica"]

CENARIOS = {
    "igual à esperada": ["consultar_pedido", "consultar_politica"],
    "com uma chamada extra": ["consultar_pedido", "consultar_pedido", "consultar_politica"],
    "ordem trocada": ["consultar_politica", "consultar_pedido"],
    "falta uma chamada": ["consultar_pedido"],
}

print(f"Esperada: {ESPERADA}\n")
print(f"{'cenário':24s} exata na_ordem qualquer prec. revoc.")
for nome, real in CENARIOS.items():
    print(f"{nome:24s} {exata(real, ESPERADA):5.2f} {na_ordem(real, ESPERADA):8.2f} "
          f"{em_qualquer_ordem(real, ESPERADA):7.2f} {precisao(real, ESPERADA):5.2f} {revocacao(real, ESPERADA):6.2f}")

print("\nUsou consultar_politica?")
for nome, real in CENARIOS.items():
    print(f"  {nome:24s} {usou_a_ferramenta(real, 'consultar_politica')}")
