import tempfile
from pathlib import Path

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

import memoria
from memoria import Contexto, Memoria
from trajetoria import mostrar

def extrator_sessao(fato_chave, fato_valor):
    def modelo(mensagens, info: AgentInfo) -> ModelResponse:
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {
            "fatos": [{"chave": fato_chave, "valor": fato_valor}]
        })])
    return modelo


def atendente_com_memoria(mensagens, info: AgentInfo) -> ModelResponse:
    if isinstance(mensagens[-1].parts[-1], ToolReturnPart):
        return ModelResponse(parts=[TextPart("Combinado: entrega à tarde, como você prefere.")])
    return ModelResponse(parts=[
        TextPart("Vou conferir suas preferências de entrega."),
        ToolCallPart("lembrar", {"tema": "período de entrega"}),
    ])


def atendente_simples(mensagens, info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart("Anotado: entregas à tarde.")])


mem = Memoria(Path(tempfile.mkdtemp()))
ctx = Contexto(mem, "lia")

print("== Sessão 1: a cliente informa uma preferência")
r1 = memoria.atendente.run_sync("Prefiro receber à tarde, de manhã não tem ninguém.",
                                model=FunctionModel(atendente_simples), deps=ctx)
with memoria.extrator.override(model=FunctionModel(extrator_sessao("periodo_entrega_preferido", "tarde"))):
    print(memoria.encerrar_sessao(mem, "lia", "s1", r1.all_messages()))

print("\n== Sessão 2: histórico vazio, mas a memória lembra")
r2 = memoria.atendente.run_sync("Quero combinar a entrega do pedido 1002.",
                                model=FunctionModel(atendente_com_memoria), deps=ctx)
mostrar(r2)

print("\n== Sessão 3: a preferência muda")
with memoria.extrator.override(model=FunctionModel(extrator_sessao("periodo_entrega_preferido", "manhã"))):
    print(memoria.encerrar_sessao(mem, "lia", "s3", r2.all_messages()))
print(mem.fatos("lia"))

print("\n== Curto prazo: retomar a sessão s1 depois de reiniciar")
retomada = mem.carregar_sessao("s1")
print("Mensagens recuperadas:", len(retomada), "| iguais às originais:", retomada == r1.all_messages())
