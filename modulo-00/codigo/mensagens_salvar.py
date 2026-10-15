from pathlib import Path

from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_ai.models.test import TestModel

atendente = Agent(TestModel(custom_output_text="Custa R$ 49,90."))
resultado = atendente.run_sync("Quanto custa o vaso de barro?")

arquivo = Path("conversa.json")
arquivo.write_bytes(ModelMessagesTypeAdapter.dump_json(resultado.all_messages()))

historico = ModelMessagesTypeAdapter.validate_json(arquivo.read_bytes())
print(type(historico[0]).__name__, type(historico[1]).__name__)
print(historico == resultado.all_messages())

continuacao = atendente.run_sync("E o de cerâmica?", message_history=historico)
print(len(continuacao.all_messages()))
arquivo.unlink()
