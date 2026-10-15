from pydantic_ai import Agent

from busca import indice
from config import MODELO

LIMIAR = 0.2


def buscar_politicas(pergunta: str) -> str:
    """Busca na base de políticas da loja. Devolve até 2 trechos, cada um com o seu id entre colchetes."""
    achados = [(p, f) for p, f in indice.buscar(pergunta, k=2) if p >= LIMIAR]
    if not achados:
        return "Nenhum trecho relevante encontrado."
    return "\n".join(f"[{f.id}] {f.texto}" for _, f in achados)


agente_rag = Agent(
    MODELO,
    tools=[buscar_politicas],
    instructions=(
        "Você atende clientes da loja Casa Verde. Responda apenas com base nos "
        "trechos devolvidos por `buscar_politicas`, citando o id do trecho entre "
        "colchetes, como [devolucao]. Se os trechos não responderem à pergunta, "
        "diga que não sabe e ofereça encaminhar a um atendente. Máximo de três frases."
    ),
)

redator = Agent(
    MODELO,
    instructions=(
        "Responda à pergunta do cliente usando apenas o contexto fornecido, citando "
        "o id do trecho entre colchetes. Se o contexto não bastar, diga que não sabe."
    ),
)


def responder_com_pipeline(pergunta: str) -> str:
    achados = [(p, f) for p, f in indice.buscar(pergunta, k=2) if p >= LIMIAR]
    contexto = "\n".join(f"[{f.id}] {f.texto}" for _, f in achados) or "(sem trechos relevantes)"
    return redator.run_sync(f"Contexto:\n{contexto}\n\nPergunta: {pergunta}").output
