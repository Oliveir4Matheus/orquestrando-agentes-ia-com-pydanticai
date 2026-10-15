from conferencia_quase_exata import igual_quase_exato, nivel

CASOS = [
    ("R$ 1.234,50", "1234.5"),
    ("1234,5", "1234.5"),
    ("12%", "12"),
    ("Em separação", "em separacao"),
    ("o pedido 1002, o pedido 1001", "pedido 1002, pedido 1001"),
    ("o pedido 1001, o pedido 1002", "pedido 1002, pedido 1001"),
    ("cerca de 90", "90"),
]

for resposta, gabarito in CASOS:
    print(f"{resposta!r:34s} vs {gabarito!r:28s} -> {igual_quase_exato(resposta, gabarito)}")

print()
for passos, ferramentas in [(3, 1), (7, 3), (18, 5)]:
    print(f"{passos:2d} passos, {ferramentas} ferramenta(s): nível {nivel(passos, ferramentas)}")
