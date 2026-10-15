from pydantic_ai.models.function import FunctionModel

from agente import agente
from modelo_roteirizado import modelo_roteirizado
from trajetoria import mostrar

resultado = agente.run_sync(
    "Compare os pedidos 1001 e 1002.", model=FunctionModel(modelo_roteirizado)
)
mostrar(resultado)
print("Chamadas ao modelo:", resultado.usage.requests)
