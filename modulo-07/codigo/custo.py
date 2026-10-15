TOKENS_DO_CHAT = 2_000  # tokens de uma interação de chat sobre a tarefa
FATORES = {"chat": 1, "agente": 4, "multiagente": 15}  # ordens de grandeza do relato da Anthropic
CUSTO_POR_MIL_TOKENS = 0.01  # valor hipotético, em reais


def custo_da_tarefa(arquitetura: str) -> float:
    return TOKENS_DO_CHAT * FATORES[arquitetura] / 1000 * CUSTO_POR_MIL_TOKENS


def vale_a_pena(valor_da_tarefa: float, arquitetura: str) -> bool:
    return valor_da_tarefa > custo_da_tarefa(arquitetura)


for arquitetura in FATORES:
    print(f"{arquitetura:12s}: R$ {custo_da_tarefa(arquitetura):.2f} por tarefa")

print()
for valor in (0.10, 2.00):
    print(f"Tarefa que vale R$ {valor:.2f}: multiagente compensa? {vale_a_pena(valor, 'multiagente')}")
