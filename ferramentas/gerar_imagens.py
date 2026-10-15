"""Gera as imagens do livro com o Gemini (via `agy`), a partir de imagens.json.

Pula as que já existem, usa 3 processos em paralelo e alterna entre as contas
quando a cota de uma esgota. Uso: python gerar_imagens.py [--uma-vez]
"""
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MANIFESTO = Path(__file__).resolve().parent / "imagens.json"
PAUSA_SEGUNDOS = 20 * 60
ESPERA_DA_CONTA = 30 * 60
COMANDOS = ["agy", "agy02"]  # contas, em ordem de preferência
PARALELISMO = 3

esgotada_ate: dict[str, float] = {}
trava = threading.Lock()


def pendentes() -> list[dict]:
    itens = json.loads(MANIFESTO.read_text())
    estilo = itens["estilo"]
    return [
        {**item, "prompt": f"{item['prompt']} {estilo} Nome do arquivo: {Path(item['arquivo']).name}"}
        for item in itens["imagens"]
        if not (RAIZ / item["arquivo"]).exists()
    ]


def gerar(item: dict) -> bool:
    destino = RAIZ / item["arquivo"]
    destino.parent.mkdir(parents=True, exist_ok=True)
    for comando in COMANDOS:
        with trava:
            if esgotada_ate.get(comando, 0) > time.time():
                continue
        proc = subprocess.run(
            [comando, "-p", item["prompt"], "--dangerously-skip-permissions"],
            cwd=destino.parent, capture_output=True, text=True, timeout=1200,
        )
        saida = proc.stdout + proc.stderr
        for sobra in destino.parent.glob("*.html"):
            sobra.unlink()
        if "RESOURCE_EXHAUSTED" in saida:
            with trava:
                esgotada_ate[comando] = time.time() + ESPERA_DA_CONTA
            print(f"Cota esgotada em {comando}.", flush=True)
            continue
        print(("OK   " if destino.exists() else "FALHA"), f"[{comando}]", item["arquivo"], flush=True)
        return destino.exists()
    return False


def main() -> None:
    uma_vez = "--uma-vez" in sys.argv
    while True:
        faltam = pendentes()
        if not faltam:
            print("Todas as imagens existem.")
            return
        print(f"{len(faltam)} imagens pendentes.", flush=True)
        with ThreadPoolExecutor(PARALELISMO) as pool:
            resultados = list(pool.map(gerar, faltam))
        if uma_vez:
            return
        if not all(resultados):
            time.sleep(PAUSA_SEGUNDOS)


if __name__ == "__main__":
    main()
