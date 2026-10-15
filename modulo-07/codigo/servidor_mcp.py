from fastmcp import FastMCP

from loja import buscar_pedido, buscar_politica

servidor = FastMCP("casa-verde")


@servidor.tool
def consultar_pedido(codigo: str) -> str:
    """Consulta o status e a previsão de entrega de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


@servidor.tool
def consultar_politica(tema: str) -> str:
    """Consulta uma política da loja. Temas: devolucao, cancelamento, frete."""
    return buscar_politica(tema) or "Tema não encontrado."


@servidor.resource("loja://politicas/devolucao")
def texto_da_politica_de_devolucao() -> str:
    """Texto oficial da política de devolução."""
    return buscar_politica("devolucao")


if __name__ == "__main__":
    servidor.run()
