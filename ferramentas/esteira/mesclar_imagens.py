"""Mescla os fragmentos de imagem de cada capítulo (esteira/imagens/<id>.json) em ferramentas/imagens.json.

Só entram fragmentos de capítulos ACEITOS (progresso.json). Não repete `arquivo` já existente no manifesto.
Depois da mesclagem, rode o gerador de sempre: python ferramentas/gerar_imagens.py
Uso: python3 mesclar_imagens.py [--simular]
"""
import fcntl
import hashlib
import json
import re
import sys
from pathlib import Path

ESTEIRA = Path(__file__).resolve().parent
LIVRO = ESTEIRA.parent.parent
MANIFESTO = LIVRO / "ferramentas" / "imagens.json"


def main() -> None:
    simular = "--simular" in sys.argv
    prog = json.loads((ESTEIRA / "progresso.json").read_text())
    dados = json.loads(MANIFESTO.read_text())
    existentes = {i["arquivo"] for i in dados["imagens"]}
    novas, ignoradas = [], []
    for frag in sorted((ESTEIRA / "imagens").glob("*.json"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.stem)] + [p.stem.endswith("p2")]):
        cid = frag.stem
        if prog.get(cid, {}).get("status") != "aceito":
            ignoradas.append(cid)
            continue
        for item in json.loads(frag.read_text()):
            if item["arquivo"] not in existentes:
                novas.append({"arquivo": item["arquivo"], "prompt": item["prompt"]})
                existentes.add(item["arquivo"])
    print(f"{len(novas)} imagens novas de capítulos aceitos; fragmentos ignorados (não aceitos): {ignoradas or 'nenhum'}")
    if simular or not novas:
        return
    dados["imagens"].extend(novas)
    MANIFESTO.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n")
    estado_arq = ESTEIRA / "estado.json"
    with open(estado_arq.with_suffix(".lock"), "w") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        estado = json.loads(estado_arq.read_text()) if estado_arq.exists() else {}
        estado["ferramentas/imagens.json"] = hashlib.sha256(MANIFESTO.read_bytes()).hexdigest()
        estado_arq.write_text(json.dumps(estado, indent=1, sort_keys=True))
    print(f"manifesto atualizado: {len(dados['imagens'])} imagens no total")


if __name__ == "__main__":
    main()
