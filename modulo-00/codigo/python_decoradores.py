registradas = {}


def ferramenta(funcao):
    registradas[funcao.__name__] = funcao.__doc__
    return funcao


@ferramenta
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código."""
    return "enviado"


print(registradas)
print(consultar_pedido("1001"))
