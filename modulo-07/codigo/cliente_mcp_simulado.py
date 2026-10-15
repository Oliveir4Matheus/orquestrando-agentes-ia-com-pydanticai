import asyncio

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from cliente_mcp import agente


def modelo(mensagens, info):
    if any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts):
        return ModelResponse(parts=[TextPart("Seu pedido 1001 foi enviado e chega em 12/10.")])
    print("Ferramentas descobertas no servidor MCP:")
    for ferramenta in info.function_tools:
        print(f"  {ferramenta.name}: {ferramenta.description}")
    return ModelResponse(parts=[ToolCallPart("consultar_pedido", {"codigo": "1001"})])


async def principal():
    resultado = await agente.run("Onde está o pedido 1001?", model=FunctionModel(modelo))
    retornos = [p.content for m in resultado.all_messages() for p in m.parts if isinstance(p, ToolReturnPart)]
    print("Retorno do servidor:", retornos[0])
    print("Resposta:", resultado.output)


asyncio.run(principal())
