from pydantic import BaseModel, Field

from pydantic_ai import Agent

from config import MODELO

CASO = (
    "Cliente recebeu um sofá com o tecido manchado, 12 dias após a entrega. "
    "Quer uma solução. O prazo de devolução da loja é de 7 dias."
)


class Opcao(BaseModel):
    nome: str
    descricao: str


class Opcoes(BaseModel):
    opcoes: list[Opcao]


class Nota(BaseModel):
    justificativa: str
    nota: int = Field(ge=0, le=10)


gerador = Agent(
    MODELO,
    output_type=Opcoes,
    instructions=(
        "Proponha exatamente três soluções distintas para o caso. Cada uma "
        "tem um nome curto e uma descrição de uma frase."
    ),
)

avaliador = Agent(
    MODELO,
    output_type=Nota,
    instructions=(
        "Avalie a solução de 0 a 10 considerando satisfação do cliente, custo "
        "para a loja e coerência com o prazo de devolução de 7 dias. "
        "Escreva a justificativa antes de dar a nota."
    ),
)


def decidir(caso: str):
    avaliadas = []
    for opcao in gerador.run_sync(caso).output.opcoes:
        veredito = avaliador.run_sync(
            f"Caso: {caso}\nSolução: {opcao.nome} — {opcao.descricao}"
        ).output
        avaliadas.append((veredito.nota, opcao, veredito.justificativa))
        print(f"{veredito.nota}/10  {opcao.nome}")
    return max(avaliadas, key=lambda item: item[0])


if __name__ == "__main__":
    nota, opcao, justificativa = decidir(CASO)
    print(f"\nEscolhida: {opcao.nome} ({nota}/10)\n{justificativa}")
