from pydantic_ai import Agent

from config import MODELO

ASSINATURA = "Equipe Casa Verde"

CASOS = [
    ("Qual é o prazo de devolução?", "conhecimento", lambda r: "7 dias" in r),
    ("O frete é grátis a partir de que valor?", "conhecimento", lambda r: "200" in r),
    ("Avise que o pedido 1001 foi enviado.", "formato", lambda r: r.rstrip().endswith(ASSINATURA)),
    ("Avise que o pedido 1002 está em separação.", "formato", lambda r: r.rstrip().endswith(ASSINATURA)),
]

SUGESTAO = {
    "conhecimento": "o modelo não tem o dado: recuperação (RAG)",
    "formato": "o modelo não conhece a convenção: melhore o prompt",
}


def diagnosticar(agente: Agent, **opcoes) -> dict[str, int]:
    falhas: dict[str, int] = {}
    totais: dict[str, int] = {}
    for pergunta, tipo, passou in CASOS:
        resposta = agente.run_sync(pergunta, **opcoes).output
        totais[tipo] = totais.get(tipo, 0) + 1
        if not passou(resposta):
            falhas[tipo] = falhas.get(tipo, 0) + 1
            print(f"FALHOU [{tipo}] {pergunta}\n        -> {resposta}")
    print()
    for tipo, total in totais.items():
        print(f"{tipo:12s}: {falhas.get(tipo, 0)} de {total} falharam")
    for tipo in falhas:
        print(f"Sugestão para {tipo}: {SUGESTAO[tipo]}")
    return falhas
