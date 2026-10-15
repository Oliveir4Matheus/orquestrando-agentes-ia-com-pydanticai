import logfire

# Registra localmente os passos do agente, sem enviar nada para fora. Os avaliadores
# de trajetória leem esses registros.
logfire.configure(send_to_logfire=False, console=False)
logfire.instrument_pydantic_ai()
