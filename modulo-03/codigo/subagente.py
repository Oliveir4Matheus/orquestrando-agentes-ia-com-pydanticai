from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ToolReturnPart

from config import MODELO
from sob_demanda import detalhar_pedido, listar_pedidos

investigador = Agent(
    MODELO,
    tools=[listar_pedidos, detalhar_pedido],
    instructions=(
        "Investigue o histórico de pedidos do cliente e responda a pergunta "
        "em no máximo duas frases, citando só os códigos relevantes."
    ),
)

principal = Agent(
    MODELO,
    instructions=(
        "Você atende clientes da loja Casa Verde. Para perguntas sobre o "
        "histórico de compras, use `investigar_historico`. Responda em até duas frases."
    ),
)


@principal.tool
async def investigar_historico(ctx: RunContext[None], pergunta: str) -> str:
    """Investiga o histórico de pedidos da cliente 'lia' e devolve um resumo curto."""
    resultado = await investigador.run(pergunta, usage=ctx.usage)
    lido = sum(
        len(str(parte.content))
        for mensagem in resultado.all_messages()
        for parte in mensagem.parts
        if isinstance(parte, ToolReturnPart)
    )
    print(f"O subagente leu {lido} caracteres; o agente principal recebe {len(resultado.output)}.")
    return resultado.output
