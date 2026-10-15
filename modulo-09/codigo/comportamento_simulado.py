"""Um 'modelo' que se comporta como um agente real e imperfeito, de forma reproduzível.

Cada pergunta tem um roteiro: as ferramentas que ele chama e a resposta final. Alguns
roteiros têm defeitos de propósito, para que as avaliações tenham o que encontrar.
"""
from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart, UserPromptPart
from pydantic_ai.models.function import FunctionModel

ROTEIROS = {
    "Onde está o pedido 1001?": ([("consultar_pedido", {"codigo": "1001"})], "Seu pedido 1001 foi enviado e chega em 12/10."),
    "Onde está o pedido 1002?": ([("consultar_pedido", {"codigo": "1002"})], "Seu pedido 1002 está em separação, com previsão para 15/10."),
    "Qual é o prazo de devolução?": ([("consultar_politica", {"tema": "devolucao"})], "Você pode devolver em até 7 dias após o recebimento."),
    "O frete é grátis acima de quanto?": ([("consultar_politica", {"tema": "frete"})], "O frete é grátis para compras acima de R$ 200."),
    "Posso cancelar o pedido 1002?": ([("consultar_pedido", {"codigo": "1002"})], "Sim: o pedido 1002 ainda está em separação e pode ser cancelado."),
    # defeito 1: responde sem consultar e erra
    "Posso cancelar o pedido 1001?": ([], "Sim, posso cancelar o pedido 1001 agora mesmo."),
    # defeito 2: deveria recusar, mas chama uma ferramenta à toa
    "Qual é a capital da França?": ([("consultar_politica", {"tema": "frete"})], "A capital da França é Paris."),
    # defeito 3: pergunta composta, mas consulta só um pedido
    "Compare os pedidos 1001 e 1002.": ([("consultar_pedido", {"codigo": "1001"})], "O pedido 1001 foi enviado."),
    "Qual é a cor do sofá?": ([], "Não posso ajudar com isso, mas posso consultar pedidos e políticas da loja."),
}


def _pergunta(mensagens) -> str:
    for mensagem in mensagens:
        for parte in mensagem.parts:
            if isinstance(parte, UserPromptPart):
                return parte.content
    raise ValueError("sem pergunta")


def roteirizado(roteiros=ROTEIROS) -> FunctionModel:
    def modelo(mensagens, info):
        chamadas, final = roteiros[_pergunta(mensagens)]
        ja_chamou = any(isinstance(p, ToolReturnPart) for m in mensagens for p in m.parts)
        if chamadas and not ja_chamou:
            return ModelResponse(parts=[ToolCallPart(nome, args) for nome, args in chamadas])
        return ModelResponse(parts=[TextPart(final)])

    return FunctionModel(modelo)
