class Caixa:
    def __enter__(self):
        print("caixa aberta")
        return self

    def __exit__(self, tipo, erro, rastro):
        print("caixa fechada")
        return False


with Caixa() as caixa:
    print("registrando venda")

try:
    with Caixa():
        raise ValueError("valor inválido")
except ValueError as erro:
    print("erro tratado:", erro)

pedidos = [("1001", 89.9), ("1002", 189.9), ("1003", 45.0)]
print(sorted(pedidos, key=lambda pedido: pedido[1]))
