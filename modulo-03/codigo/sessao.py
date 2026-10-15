from pydantic_ai.models.function import FunctionModel

from modelo_atendente import modelo_atendente

PERGUNTAS = [
    "Onde está o pedido 1001?",
    "E o pedido 1002?",
    "E o pedido 1003?",
    "Voltando ao 1001, quando chega?",
    "E o 1002, quando chega?",
]


def conversar(agente, perguntas=PERGUNTAS):
    historico = []
    for numero, pergunta in enumerate(perguntas, start=1):
        resultado = agente.run_sync(
            pergunta, model=FunctionModel(modelo_atendente), message_history=historico
        )
        historico = resultado.all_messages()
        print(f"Turno {numero}: {len(historico):2d} mensagens, {resultado.usage.input_tokens} tokens de entrada")
    return historico
