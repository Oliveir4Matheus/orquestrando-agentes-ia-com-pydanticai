"""Espera os `worker_done` de uma Run do Orca, sem poluir o contexto de quem chama.

Uso: python3 esperar.py --esperados N [--limite-s 3000] [--saida resultados.json]
Imprime uma linha por evento relevante (worker_done, question, escalation); heartbeats são só confirmados.
Sai quando N `worker_done` chegarem, quando houver `question`/`escalation` (para o coordenador responder) ou no limite.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

CLI = "orca-ide"


def orca(*args: str, tempo: int = 700) -> dict:
    r = subprocess.run([CLI, *args, "--json"], capture_output=True, text=True, timeout=tempo)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "raw": (r.stdout + r.stderr)[-300:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--esperados", type=int, required=True)
    ap.add_argument("--limite-s", type=int, default=3000)
    ap.add_argument("--saida", default="resultados.json")
    ap.add_argument("--manter", action="store_true", help="não liberar os workers ao terminar")
    a = ap.parse_args()
    saida = Path(a.saida)
    resultados = json.loads(saida.read_text()) if saida.exists() else {}
    inicio, ack = time.time(), None
    tipos = "worker_done,escalation,question"
    while len(resultados) < a.esperados and time.time() - inicio < a.limite_s:
        args = ["orchestration", "check"] + (["--ack", ack] if ack else []) + ["--wait", "--types", tipos, "--timeout-ms", "240000"]
        r = orca(*args)
        ack = None
        if not r.get("ok"):
            print("erro no check:", r.get("raw") or r.get("error"))
            time.sleep(10)
            continue
        res = r["result"]
        ack = res.get("deliveryId")
        parar = False
        for m in res.get("messages", []):
            tipo = m.get("type")
            try:
                carga = json.loads(m["payload"]) if m.get("payload") else {}
            except (TypeError, json.JSONDecodeError):
                carga = {}
            if tipo == "worker_done":
                chave = carga.get("taskId") or m["id"]
                resultados[chave] = {"assunto": m.get("subject"), "corpo": m.get("body"), "carga": carga, "quando": m.get("created_at")}
                print(f"[worker_done] {chave} | {carga.get('outcome')} | {m.get('subject')} | arquivos: {carga.get('filesModified') or carga.get('files_modified')}")
            elif tipo in ("question", "escalation"):
                print(f"[{tipo}] id={m['id']} de={m.get('from_handle')} | {m.get('subject')} | {(m.get('body') or '')[:300]}")
                parar = True
        saida.write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
        if parar:
            if ack:
                orca("orchestration", "check", "--ack", ack, "--timeout-ms", "1000")
            return 2
    if ack:
        orca("orchestration", "check", "--ack", ack, "--timeout-ms", "1000")
    if not a.manter:
        for chave, v in resultados.items():
            did = v["carga"].get("dispatchId")
            if did and not v.get("liberado"):
                rel = orca("orchestration", "worker-release", "--dispatch", did)
                v["liberado"] = bool(rel.get("ok"))
        saida.write_text(json.dumps(resultados, ensure_ascii=False, indent=1))
    print(f"{len(resultados)}/{a.esperados} worker_done recebidos em {int(time.time() - inicio)} s")
    return 0 if len(resultados) >= a.esperados else 1


if __name__ == "__main__":
    sys.exit(main())
