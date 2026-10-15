from pydantic_ai import Agent, ModelRetry

from config import MODELO
from executor import ErroDeExecucao, executar
from ferramentas import detalhar_pedido, listar_pedidos

FERRAMENTAS = {"listar_pedidos": listar_pedidos, "detalhar_pedido": detalhar_pedido}

agente_json = Agent(
    MODELO,
    tools=[listar_pedidos, detalhar_pedido],
    instructions="Você atende clientes da loja Casa Verde. Use as ferramentas e responda em uma frase.",
)

INSTRUCOES_CODIGO = """\
Você atende clientes da loja Casa Verde. Para consultar dados, escreva código
Python e execute-o com `executar_codigo`. Use print() para ver resultados.
Funções disponíveis:

- listar_pedidos(cliente: str) -> list[dict]: itens com `codigo`, `status` e `data`.
- detalhar_pedido(cliente: str, codigo: str) -> dict: `status`, `data` e `itens`
  (texto, como '3x caneca; ...').

Você pode usar variáveis, laços, condicionais e operações com texto, números e
listas. Não há imports nem acesso a arquivos. Imprima só o resultado final.
Responda ao cliente em uma frase.
"""

agente_codigo = Agent(MODELO, instructions=INSTRUCOES_CODIGO)


@agente_codigo.tool_plain
def executar_codigo(codigo: str) -> str:
    """Executa um trecho de Python e devolve o que ele imprimiu com print()."""
    try:
        return executar(codigo, FERRAMENTAS) or "(sem saída: use print para mostrar o resultado)"
    except ErroDeExecucao as erro:
        raise ModelRetry(str(erro)) from None
