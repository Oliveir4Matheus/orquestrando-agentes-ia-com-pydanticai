from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import arvore


def modelo_gerador(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"opcoes": [
        {"nome": "Reembolso integral", "descricao": "Devolver todo o valor do sofá."},
        {"nome": "Reparo do tecido", "descricao": "Enviar um técnico para tratar a mancha."},
        {"nome": "Vale-compra", "descricao": "Oferecer crédito de 30% para uma próxima compra."},
    ]})])


NOTAS = {
    "Reembolso integral": (3, "Atende o cliente, mas ignora o prazo e tem custo alto."),
    "Reparo do tecido": (8, "Resolve o defeito sem violar o prazo e com custo moderado."),
    "Vale-compra": (5, "Custo baixo, mas não resolve a mancha."),
}


def modelo_avaliador(mensagens, info: AgentInfo) -> ModelResponse:
    prompt = mensagens[-1].parts[0].content
    nome = next(n for n in NOTAS if n in prompt)
    nota, justificativa = NOTAS[nome]
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
        "justificativa": justificativa, "nota": nota,
    })])


with arvore.gerador.override(model=FunctionModel(modelo_gerador)), \
        arvore.avaliador.override(model=FunctionModel(modelo_avaliador)):
    nota, opcao, justificativa = arvore.decidir(arvore.CASO)
print(f"\nEscolhida: {opcao.nome} ({nota}/10)\n{justificativa}")
