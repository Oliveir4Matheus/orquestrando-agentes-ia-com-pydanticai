import asyncio

import modelos_simulados as sim
import paralelo

MENSAGEM = "Meu pedido atrasou e ninguém responde. Meu e-mail é lia@exemplo.com."


async def principal():
    with paralelo.agente_sentimento.override(model=sim.saida({"valor": "negativo"}, espera=0.3)), \
            paralelo.agente_categoria.override(model=sim.saida({"valor": "entrega"}, espera=0.3)), \
            paralelo.agente_pii.override(model=sim.saida({"contem": True}, espera=0.3)):
        sequencial, t_seq = await paralelo.cronometrar(paralelo.analisar_em_sequencia, MENSAGEM)
        simultaneo, t_par = await paralelo.cronometrar(paralelo.analisar, MENSAGEM)

    print("Resultado:", simultaneo)
    print("Mesmo resultado nas duas formas:", sequencial == simultaneo)
    print(f"Em sequência: {t_seq:.1f} s | em paralelo: {t_par:.1f} s")


asyncio.run(principal())
