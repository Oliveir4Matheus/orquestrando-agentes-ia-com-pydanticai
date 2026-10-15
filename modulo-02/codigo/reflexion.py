from pydantic_ai import Agent

from config import MODELO
from loja import buscar_pedido

PEDIDO = buscar_pedido("1002")
TAREFA = (
    "Escreva uma mensagem de até 160 caracteres para o cliente informando o "
    f"status e a previsão de entrega do pedido 1002. Dados: {PEDIDO}"
)

ator = Agent(
    MODELO,
    instructions="Você escreve mensagens de atendimento da loja Casa Verde. Responda apenas com a mensagem.",
)

reflexor = Agent(
    MODELO,
    instructions=(
        "Você recebe uma tarefa, a tentativa feita e as falhas apontadas. "
        "Escreva UMA lição curta, no imperativo, que ajude a próxima tentativa."
    ),
)


def avaliar(mensagem: str) -> list[str]:
    falhas = []
    if len(mensagem) > 160:
        falhas.append(f"a mensagem tem {len(mensagem)} caracteres; o limite é 160")
    if "15/10" not in mensagem:
        falhas.append("a previsão 15/10 não aparece")
    if not mensagem.rstrip().endswith("Equipe Casa Verde"):
        falhas.append("a mensagem não termina com a assinatura padrão da loja")
    return falhas


def resolver(max_tentativas: int = 3) -> str | None:
    licoes: list[str] = []
    for numero in range(1, max_tentativas + 1):
        prompt = TAREFA
        if licoes:
            prompt += "\n\nLições de tentativas anteriores:\n"
            prompt += "\n".join(f"- {licao}" for licao in licoes[-3:])

        tentativa = ator.run_sync(prompt).output
        falhas = avaliar(tentativa)
        print(f"Tentativa {numero}: {tentativa}")

        if not falhas:
            print("Aprovada.")
            return tentativa

        print("Falhas:", "; ".join(falhas))
        licao = reflexor.run_sync(
            f"Tarefa: {TAREFA}\nTentativa: {tentativa}\nFalhas: {'; '.join(falhas)}"
        ).output
        print("Lição:", licao)
        licoes.append(licao)

    print("Sem aprovação após", max_tentativas, "tentativas.")
    return None


if __name__ == "__main__":
    resolver()
