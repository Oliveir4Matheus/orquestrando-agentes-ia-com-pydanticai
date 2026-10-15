import tempfile
from pathlib import Path

from idempotencia import Livro

REEMBOLSOS: list[str] = []


def reembolsar(livro: Livro, id_da_chamada: str, pedido: str, valor: float) -> str:
    def efeito():
        REEMBOLSOS.append(pedido)
        return f"reembolso de R$ {valor:.2f} registrado para o pedido {pedido}"

    return livro.executar_uma_vez(id_da_chamada, efeito)


livro = Livro(Path(tempfile.mkdtemp()) / "efeitos.json")

print(reembolsar(livro, "chamada-77", "1001", 120.0))
print("Retentativa da mesma chamada:", reembolsar(livro, "chamada-77", "1001", 120.0))
print("Reembolsos efetivamente feitos:", REEMBOLSOS)

livro_reaberto = Livro(livro.arquivo)  # o processo reiniciou
print("Depois do reinício:", reembolsar(livro_reaberto, "chamada-77", "1001", 120.0))
print("Reembolsos efetivamente feitos:", REEMBOLSOS)
