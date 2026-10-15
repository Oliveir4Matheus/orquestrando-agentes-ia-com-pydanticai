from collections import Counter

from cot import PERGUNTA, raciocinado


def votar(pergunta: str, tentativas: int = 5):
    valores = [round(raciocinado.run_sync(pergunta).output.valor, 2) for _ in range(tentativas)]
    valor, votos = Counter(valores).most_common(1)[0]
    return valor, votos, valores


if __name__ == "__main__":
    valor, votos, valores = votar(PERGUNTA)
    print("Respostas:", valores)
    print(f"Mais votada: R$ {valor:.2f} ({votos} de {len(valores)})")
