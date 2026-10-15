import re

import encadeamento
import modelos_simulados as sim


def extrair(mensagens):
    texto = sim.prompt_do_usuario(mensagens)
    achado = re.search(r"\d{4}", texto)
    return {
        "codigo_pedido": achado.group() if achado else None,
        "problema": "pedido atrasado",
        "urgencia": "alta",
    }


MENSAGENS = [
    "O pedido 1001 está atrasado e preciso dele hoje!",
    "Meu pedido está atrasado!",
    "O pedido 9999 está atrasado!",
]

with encadeamento.extrator.override(model=sim.saida(extrair, "extrator")), \
        encadeamento.redator.override(model=sim.texto(
            "Seu pedido 1001 foi enviado e chega em 12/10. Equipe Casa Verde", "redator")):
    for mensagem in MENSAGENS:
        sim.CHAMADAS.clear()
        print(mensagem)
        print("  ->", encadeamento.atender(mensagem))
        print("  chamadas ao modelo:", sim.CHAMADAS)
