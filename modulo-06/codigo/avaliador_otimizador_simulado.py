import avaliador_otimizador as ao
import modelos_simulados as sim

RECLAMACAO = "O vaso chegou quebrado e ninguém me respondeu."


def redigir(mensagens):
    if "Problemas apontados" in sim.prompt_do_usuario(mensagens):
        return ("Sinto muito pelo vaso quebrado e pela demora. Vou abrir uma solicitação "
                "de troca agora, e nossa equipe retornará por e-mail com os próximos passos.")
    return "Garantimos o reembolso total em 24 horas. Obrigado pelo contato."


def avaliar(mensagens):
    if "reembolso total" in sim.prompt_do_usuario(mensagens):
        return {"problemas": ["não reconhece o problema com empatia",
                              "promete reembolso e prazo não confirmados"],
                "aprovado": False}
    return {"problemas": [], "aprovado": True}


with ao.redator.override(model=sim.texto(redigir)), ao.avaliador.override(model=sim.saida(avaliar)):
    resultado = ao.melhorar(RECLAMACAO)

print(f"\nAprovado: {resultado.aprovado} em {resultado.rodadas} rodadas")
print(resultado.texto)
