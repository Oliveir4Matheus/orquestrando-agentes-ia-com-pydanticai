from pydantic_ai.models.function import FunctionModel

from agente import agente
from espiar_historico import espiar_historico

modelo = FunctionModel(espiar_historico)

primeira = agente.run_sync("Onde está o meu pedido 1001?", model=modelo)
segunda = agente.run_sync(
    "E qual é o valor dele?", model=modelo, message_history=primeira.new_messages()
)
print("Mensagens na conversa:", len(segunda.all_messages()))
