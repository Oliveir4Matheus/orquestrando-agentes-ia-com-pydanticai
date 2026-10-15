from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import ancoragem


def modelo_redator(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart(
        "Você pode devolver em até 7 dias corridos [devolucao]. "
        "O reembolso cai na sua conta em 24 horas."
    )])


def modelo_verificador(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"afirmacoes": [
        {"texto": "Você pode devolver em até 7 dias corridos [devolucao].", "trecho_id": "devolucao"},
        {"texto": "O reembolso cai na sua conta em 24 horas.", "trecho_id": None},
    ]})])


with ancoragem.redator.override(model=FunctionModel(modelo_redator)), \
        ancoragem.verificador.override(model=FunctionModel(modelo_verificador)):
    for pergunta in ["Posso devolver o produto depois de 10 dias?", "Qual a cor do sofá?"]:
        resposta = ancoragem.responder_ancorado(pergunta)
        print(pergunta)
        print("  texto    :", resposta.texto)
        print("  citações :", resposta.citacoes)
        print(f"  suporte  : {resposta.suporte:.2f} | revisada: {resposta.revisada}")
