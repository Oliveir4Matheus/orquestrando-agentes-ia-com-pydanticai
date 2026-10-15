import logfire
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

COLETOR = InMemorySpanExporter()

# Os passos do agente ficam registrados em memória; nada sai do processo.
logfire.configure(
    send_to_logfire=False,
    console=False,
    additional_span_processors=[SimpleSpanProcessor(COLETOR)],
)
logfire.instrument_pydantic_ai()


def arvore_do_rastro() -> list[str]:
    """Reconstrói a árvore de passos (quem chamou quem) a partir dos registros coletados."""
    spans = sorted(COLETOR.get_finished_spans(), key=lambda s: s.start_time)
    filhos: dict[int | None, list] = {}
    for span in spans:
        pai = span.parent.span_id if span.parent else None
        filhos.setdefault(pai, []).append(span)

    linhas: list[str] = []

    def descrever(span) -> str:
        atributos = span.attributes or {}
        if span.name.startswith("invoke_agent"):
            tokens = atributos.get("gen_ai.aggregated_usage.input_tokens", 0) + atributos.get(
                "gen_ai.aggregated_usage.output_tokens", 0
            )
            return f"agente {atributos.get('gen_ai.agent.name')} ({tokens} tokens)"
        if span.name.startswith("execute_tool"):
            return f"ferramenta {atributos.get('gen_ai.tool.name')} {atributos.get('gen_ai.tool.call.arguments')}"
        return "chamada ao modelo"

    def percorrer(pai, nivel: int) -> None:
        for span in filhos.get(pai, []):
            linhas.append("  " * nivel + descrever(span))
            percorrer(span.context.span_id, nivel + 1)

    percorrer(None, 0)
    return linhas
