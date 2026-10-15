import asyncio
import time


async def consultar(codigo: str) -> str:
    await asyncio.sleep(1)
    return f"{codigo}: enviado"


async def principal() -> None:
    inicio = time.perf_counter()
    print(await consultar("1001"))
    print(await consultar("1002"))
    print(f"em sequência: {time.perf_counter() - inicio:.0f} s")

    inicio = time.perf_counter()
    respostas = await asyncio.gather(consultar("1001"), consultar("1002"))
    print(respostas)
    print(f"com gather: {time.perf_counter() - inicio:.0f} s")


asyncio.run(principal())
corotina = consultar("1003")
print(type(corotina).__name__)
corotina.close()
