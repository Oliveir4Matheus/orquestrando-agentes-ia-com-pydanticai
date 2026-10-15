from contextlib import ExitStack

import modelos_simulados as sim
import roteamento

PERGUNTAS = {
    "Onde está o pedido 1001?": "pedido",
    "Qual é o prazo de devolução?": "politica",
    "O vaso chegou quebrado, estou muito chateada.": "reclamacao",
    "Vocês têm loja física?": "outro",
}


def classificar(mensagens):
    return {"categoria": PERGUNTAS[sim.prompt_do_usuario(mensagens)]}


with ExitStack() as pilha:
    pilha.enter_context(roteamento.classificador.override(model=sim.saida(classificar)))
    for categoria, agente in roteamento.ESPECIALISTAS.items():
        pilha.enter_context(agente.override(model=sim.texto(f"[especialista: {categoria}]")))

    for pergunta in PERGUNTAS:
        categoria, resposta = roteamento.atender(pergunta)
        print(f"{pergunta:48s} -> {categoria:10s} {resposta}")
