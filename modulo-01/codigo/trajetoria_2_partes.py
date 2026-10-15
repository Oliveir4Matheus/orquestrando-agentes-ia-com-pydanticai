from pydantic_ai.models.function import FunctionModel

from agente import agente
from modelo_roteirizado import modelo_roteirizado

resultado = agente.run_sync(
    "Compare os pedidos 1001 e 1002.", model=FunctionModel(modelo_roteirizado)
)

for posicao, mensagem in enumerate(resultado.all_messages(), start=1):
    print(posicao, type(mensagem).__name__)
    for parte in mensagem.parts:
        print("   ", parte.part_kind)
