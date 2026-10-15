from pydantic_ai.models.function import FunctionModel

from agente import agente
from modelo_roteirizado import modelo_roteirizado

resultado = agente.run_sync(
    "Compare os pedidos 1001 e 1002.", model=FunctionModel(modelo_roteirizado)
)

mensagens = resultado.all_messages()
print("Mensagens na conversa:", len(mensagens))
