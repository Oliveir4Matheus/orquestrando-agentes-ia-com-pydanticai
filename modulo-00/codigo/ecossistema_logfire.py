import logfire
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

memoria = InMemorySpanExporter()
logfire.configure(
    send_to_logfire=False,
    console=False,
    additional_span_processors=[SimpleSpanProcessor(memoria)],
)
logfire.instrument_pydantic_ai()

atendente = Agent(TestModel(), name="atendente")


@atendente.tool_plain
def consultar_pedido(codigo: str) -> str:
    """Consulta o status de um pedido pelo código."""
    return "enviado"


print(atendente.run_sync("Onde está o pedido 1001?").output)
for trecho in memoria.get_finished_spans():
    print(trecho.name)
