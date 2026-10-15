def frete(valor: float, cep: str | None = None) -> float:
    if cep is None:
        return 0.0
    return 25.0 if valor < 200 else 0.0


print(frete(189.90, "01001-000"))
print(frete(189.90))
print(frete.__annotations__)

try:
    frete("caro", "01001-000")
except TypeError as erro:
    print("TypeError:", erro)
