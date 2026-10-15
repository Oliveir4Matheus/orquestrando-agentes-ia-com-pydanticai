"""Orquestrador da esteira: um worker (instância do Claude via Orca) por capítulo.

- Uma fila por módulo: os capítulos de um módulo rodam em sequência (cada um reaproveita o código do anterior);
  módulos diferentes rodam em paralelo, até --paralelo workers ao mesmo tempo.
- Depois de cada `worker_done`, o validador roda por conta própria (não confia no relato do worker).
  Aprovado -> aceita e libera o worker. Reprovado -> devolve as falhas ao mesmo worker (até 2 vezes).
- Se o processo do worker cair, recomeça a tarefa com `--retry-of` (até 2 vezes).
- É retomável: `progresso.json` guarda o que já foi aceito.

Uso: python3 orquestrar.py --modulos 0,1,2 [--paralelo 5] [--padrao claude-sonnet-5-5:medium] [--lane0 claude-opus-5-5:medium]
"""
import argparse
import json
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

ESTEIRA = Path(__file__).resolve().parent
LIVRO = ESTEIRA.parent.parent
WT = "id:a319dbc2-0e29-45ce-bc3b-d1a52ea61e6c::" + str(LIVRO)
PROGRESSO = ESTEIRA / "progresso.json"
LOG = ESTEIRA / "orquestrador.log"
MAX_TENTATIVAS = 2


def orca(*args: str, tempo: int = 700) -> dict:
    r = subprocess.run(["orca-ide", *args, "--json"], capture_output=True, text=True, timeout=tempo)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "raw": (r.stdout + r.stderr)[-300:]}


def achar(obj, chave):
    if isinstance(obj, dict):
        if chave in obj:
            return obj[chave]
        for v in obj.values():
            r = achar(v, chave)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = achar(v, chave)
            if r is not None:
                return r
    return None


def log(msg: str) -> None:
    linha = f"{time.strftime('%H:%M:%S')} {msg}"
    print(linha, flush=True)
    with LOG.open("a") as f:
        f.write(linha + "\n")


def validar(cid: str, raiz: str, aceitar: bool) -> tuple[bool, str]:
    cmd = ["python3", str(ESTEIRA / "validar.py"), cid, "--raiz", raiz] + (["--aceitar"] if aceitar else [])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    linhas = r.stdout.strip().splitlines()
    return (r.returncode == 0, "\n".join(linhas)[-1800:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modulos", required=True)
    ap.add_argument("--paralelo", type=int, default=5)
    ap.add_argument("--padrao", default="claude-sonnet-5-5:medium")
    ap.add_argument("--lane0", default="claude-opus-5-5:medium")
    ap.add_argument("--raiz", default=str(LIVRO))
    ap.add_argument("--limite-s", type=int, default=7200)
    ap.add_argument("--passe2", action="store_true", help="passe 2: anotar o código central (ids <n>p2, sem Módulo 0)")
    a = ap.parse_args()

    mapa = json.loads((ESTEIRA / "mapa.json").read_text())
    contrato = json.loads((ESTEIRA / "contrato.json").read_text())
    prog = json.loads(PROGRESSO.read_text()) if PROGRESSO.exists() else {}
    lanes: dict[int, deque] = {}
    for m in [int(x) for x in a.modulos.split(",")]:
        ids = [c["id"] for c in contrato["modulo0"]] if m == 0 else [c["id"] for c in mapa["capitulos"] if c["modulo"] == m]
        if a.passe2:
            ids = [] if m == 0 else [i + "p2" for i in ids]
        fila = deque(i for i in ids if prog.get(i, {}).get("status") != "aceito")
        if fila:
            lanes[m] = fila
    ativos: dict[str, dict] = {}  # task_id -> info

    def modelo_da(m: int) -> tuple[str, str]:
        mod, esf = (a.lane0 if m == 0 else a.padrao).split(":")
        return mod, esf

    def iniciar(m: int, cid: str, retry_of: str | None = None, task: str | None = None, tentativas: int = 0) -> None:
        mod, esf = modelo_da(m)
        if task is None:
            spec = (f"Leia o arquivo {ESTEIRA}/tarefas/{cid}.md e execute-o integralmente (ele manda ler também "
                    f"{ESTEIRA}/padrao.md). Trabalhe SOMENTE dentro da raiz de trabalho indicada nesse arquivo. "
                    f"Ao terminar, reporte com worker_done.")
            t = orca("orchestration", "task-create", "--spec", spec)
            task = achar(t.get("result", {}), "id") if t.get("ok") else None
            if not task or not str(task).startswith("task_"):
                task = (t.get("result", {}).get("task") or {}).get("id")
        args = ["orchestration", "worker-start", "--task", task, "--worktree", WT, "--agent", "claude", "--model", mod, "--effort", esf]
        if retry_of:
            args += ["--retry-of", retry_of]
        w = orca(*args)
        if not w.get("ok"):
            log(f"ERRO ao iniciar {cid}: {w.get('error') or w.get('raw')}")
            prog[cid] = {"status": "falhou_ao_iniciar"}
            lanes[m].popleft() if lanes[m] and lanes[m][0] == cid else None
            return
        did = achar(w["result"], "dispatch_id") or achar(w["result"], "dispatchId")
        ativos[task] = {"cid": cid, "m": m, "did": did, "tentativas": tentativas, "modelo": f"{mod.split('-')[1]}-{esf}"}
        log(f"INICIOU {cid} ({mod}:{esf}) task={task} tentativa={tentativas + 1}")

    def concluir(info: dict, task: str, status: str) -> None:
        cid, m = info["cid"], info["m"]
        prog[cid] = {"status": status, "modelo": info["modelo"], "tentativas": info["tentativas"] + 1}
        PROGRESSO.write_text(json.dumps(prog, indent=1, ensure_ascii=False))
        if info.get("did"):
            orca("orchestration", "worker-release", "--dispatch", info["did"])
        ativos.pop(task, None)
        if lanes[m] and lanes[m][0] == cid:
            lanes[m].popleft()
        log(f"{'ACEITO' if status == 'aceito' else 'PRECISA REVISÃO'} {cid} [{info['modelo']}]")

    def corrigir(info: dict, task: str, falhas: str) -> bool:
        wk = orca("orchestration", "worker-show", "--dispatch", info["did"])
        handle = achar(wk.get("result", {}), "agent_terminal_handle")
        if not handle or info["tentativas"] >= MAX_TENTATIVAS:
            return False
        info["tentativas"] += 1
        texto = ("O validador independente REPROVOU o seu trabalho:\n" + falhas +
                 "\nCorrija apenas as suas adições (sem tocar no conteúdo original), rode o validador de novo e termine quando aparecer APROVADO.")
        orca("terminal", "send", "--terminal", handle, "--text", texto.replace("\n", " ⏎ "), "--enter")
        time.sleep(25)
        orca("terminal", "wait", "--terminal", handle, "--for", "tui-idle", "--timeout-ms", "900000", tempo=950)
        return True

    inicio, ultima_poll = time.time(), 0.0
    while (lanes and any(lanes.values())) or ativos:
        if time.time() - inicio > a.limite_s:
            log("limite de tempo atingido")
            break
        # preencher vagas: a fila do Módulo 0 tem prioridade (é a mais longa)
        for m in sorted(lanes):
            if len(ativos) >= a.paralelo:
                break
            if lanes[m] and not any(i["m"] == m for i in ativos.values()):
                iniciar(m, lanes[m][0])
        if not ativos:
            break
        r = orca("orchestration", "check", "--wait", "--types", "worker_done,escalation,question", "--timeout-ms", "120000", tempo=200)
        res = r.get("result", {}) if r.get("ok") else {}
        for msg in res.get("messages", []):
            tipo = msg.get("type")
            try:
                carga = json.loads(msg["payload"]) if msg.get("payload") else {}
            except (TypeError, json.JSONDecodeError):
                carga = {}
            task = carga.get("taskId")
            if tipo in ("question", "escalation"):
                log(f"{tipo.upper()} de {msg.get('from_handle')}: {(msg.get('body') or msg.get('subject') or '')[:300]}")
                continue
            if tipo != "worker_done" or task not in ativos:
                continue
            info = ativos[task]
            ok, saida = validar(info["cid"], a.raiz, aceitar=True)
            while not ok and corrigir(info, task, saida):
                ok, saida = validar(info["cid"], a.raiz, aceitar=True)
            if ok:
                concluir(info, task, "aceito")
            else:
                log(f"REPROVADO {info['cid']}:\n{saida}")
                concluir(info, task, "precisa_revisao")
        if res.get("deliveryId"):
            orca("orchestration", "check", "--ack", res["deliveryId"], "--timeout-ms", "1000", tempo=30)
        # workers que caíram sem reportar
        if time.time() - ultima_poll > 90:
            ultima_poll = time.time()
            tl = orca("orchestration", "task-list")
            for t in (tl.get("result", {}).get("tasks") or []):
                tid = t.get("id")
                if tid in ativos and t.get("status") == "failed":
                    info = ativos.pop(tid)
                    if info["tentativas"] < MAX_TENTATIVAS:
                        log(f"worker de {info['cid']} caiu; recomeçando")
                        iniciar(info["m"], info["cid"], retry_of=info["did"], task=tid, tentativas=info["tentativas"] + 1)
                    else:
                        prog[info["cid"]] = {"status": "falhou"}
                        if lanes[info["m"]] and lanes[info["m"]][0] == info["cid"]:
                            lanes[info["m"]].popleft()
                        log(f"DESISTIU de {info['cid']}")
        PROGRESSO.write_text(json.dumps(prog, indent=1, ensure_ascii=False))
    resumo = {}
    for v in prog.values():
        resumo[v["status"]] = resumo.get(v["status"], 0) + 1
    log(f"FIM: {resumo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
