from pydantic_ai import ToolCallPart
from pydantic_ai.messages import RetryPromptPart

CASOS = [
    ("Onde está o pedido 1001?", "consultar_pedido", {"codigo": "1001"}),
    ("Cadê o #1002?", "consultar_pedido", {"codigo": "1002"}),
    ("Qual o prazo de devolução?", "consultar_politica", {"tema": "devolucao"}),
    ("O frete é grátis?", "consultar_politica", {"tema": "frete"}),
]


def avaliar(agente, casos=CASOS, **opcoes) -> float:
    acertos = 0
    for pergunta, ferramenta, argumentos in casos:
        mensagens = agente.run_sync(pergunta, **opcoes).all_messages()
        chamadas = [
            (parte.tool_name, parte.args_as_dict())
            for mensagem in mensagens
            for parte in mensagem.parts
            if isinstance(parte, ToolCallPart)
        ]
        erros = sum(
            isinstance(parte, RetryPromptPart) for mensagem in mensagens for parte in mensagem.parts
        )
        primeira = chamadas[0] if chamadas else None
        ok = primeira == (ferramenta, argumentos)
        acertos += ok
        detalhe = "" if ok else f" (esperado {ferramenta}{argumentos}, recebeu {primeira})"
        print(f"{'OK  ' if ok else 'ERRO'} {pergunta}{detalhe} | correções pedidas: {erros}")
    taxa = acertos / len(casos)
    print(f"Acerto na primeira chamada: {acertos}/{len(casos)}")
    return taxa
