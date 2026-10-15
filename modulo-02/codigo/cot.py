from pydantic import BaseModel

from pydantic_ai import Agent

from config import MODELO

PERGUNTA = (
    "Comprei 3 canecas de R$ 64,50 cada, com 10% de desconto sobre o total das "
    "canecas, e 1 vaso de R$ 189,90. Devolvi 2 canecas. O reembolso é proporcional "
    "ao valor efetivamente pago por caneca. Qual é o valor do reembolso?"
)


class Reembolso(BaseModel):
    passos: list[str]
    valor: float


direto = Agent(
    MODELO,
    output_type=float,
    instructions="Responda apenas com o valor em reais.",
)

raciocinado = Agent(
    MODELO,
    output_type=Reembolso,
    instructions=(
        "Calcule o reembolso. Preencha `passos` com o cálculo, um passo por "
        "linha, e só depois informe `valor`."
    ),
)

if __name__ == "__main__":
    print("Direto:", direto.run_sync(PERGUNTA).output)

    resposta = raciocinado.run_sync(PERGUNTA).output
    for passo in resposta.passos:
        print("-", passo)
    print("Valor:", resposta.valor)
