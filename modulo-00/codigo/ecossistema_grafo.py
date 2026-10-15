import asyncio

from pydantic_graph import GraphBuilder, StepContext

g = GraphBuilder(input_type=str, output_type=str)


@g.step
async def consultar(ctx: StepContext[None, None, str]) -> str:
    pedidos = {"1002": "em separação", "1001": "enviado"}
    return pedidos.get(ctx.inputs, "desconhecido")


@g.step
async def responder(ctx: StepContext[None, None, str]) -> str:
    return f"Status do pedido: {ctx.inputs}"


g.add(
    g.edge_from(g.start_node).to(consultar),
    g.edge_from(consultar).to(responder),
    g.edge_from(responder).to(g.end_node),
)
grafo = g.build()

print(asyncio.run(grafo.run(inputs="1002")))
print(grafo)
