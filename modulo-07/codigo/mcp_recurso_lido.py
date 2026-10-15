import asyncio

from fastmcp import Client

from servidor_mcp import servidor


async def principal():
    async with Client(servidor) as cliente:
        recursos = await cliente.list_resources()
        print("Recursos publicados:", [str(r.uri) for r in recursos])
        conteudo = await cliente.read_resource("loja://politicas/devolucao")
        print("Texto lido:", conteudo[0].text)


asyncio.run(principal())
