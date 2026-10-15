from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido

INSTRUCOES = """\
Você é o atendente virtual da loja Casa Verde. Siga esta rotina:

1. Se o cliente não informou o código do pedido, peça o código e pare.
2. Consulte o pedido com `consultar_pedido`.
3. Se o cliente quer cancelar:
   - pedido "em separação": use `cancelar_pedido` e confirme o cancelamento;
   - qualquer outro status: explique que o cancelamento não é possível e
     oriente a solicitar devolução depois da entrega.
4. Se o código não existir, diga isso e peça que o cliente confira o número.
5. Responda em português, em até três frases.
"""

suporte = Agent(MODELO, instructions=INSTRUCOES)


@suporte.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código de quatro dígitos."""
    pedido = buscar_pedido(codigo)
    return str(pedido) if pedido else "Pedido não encontrado."


@suporte.tool_plain
def cancelar_pedido(codigo: str) -> str:
    """Cancela um pedido que ainda está em separação."""
    pedido = buscar_pedido(codigo)
    if pedido is None or pedido["status"] != "em separação":
        return "Cancelamento não permitido."
    pedido["status"] = "cancelado"
    return f"Pedido {codigo} cancelado."


if __name__ == "__main__":
    print(suporte.run_sync("Quero cancelar o pedido 1002.").output)
