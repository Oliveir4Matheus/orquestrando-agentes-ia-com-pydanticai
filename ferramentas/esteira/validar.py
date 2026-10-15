"""Validador da esteira: confere, sem usar LLM, o trabalho de um capítulo.

Uso: python3 validar.py <id> [--raiz DIR] [--original DIR] [--aceitar] [--sem-links-modulo0]
  <id>: número do capítulo (ex. 11) ou capítulo do Módulo 0 (ex. 0.4)
Sai com código 0 e a palavra APROVADO quando todos os portões passam.
"""
import argparse
import ast
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ESTEIRA = Path(__file__).resolve().parent
LIVRO = ESTEIRA.parent.parent
PROJETO = LIVRO.parent
ORIGINAL = PROJETO / "scratch" / "livro-original"
VENV_PY = PROJETO / ".venv" / "bin" / "python"
FENCE_ABRE = re.compile(r"^```(\w*)\s*$")
ROTULO = re.compile(r"^\*([\w./-]+\.py)\*$")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌]")
SECOES_RELATORIO = ["Inventário", "Lacunas encontradas", "O que foi adicionado",
                    "Correções factuais sugeridas (não aplicadas)", "Imagens propostas"]
SINONIMOS_PY = {"anotação de tipo": ["type hint", "anotaç", "dica de tipo"], "docstring": ["docstring"], "lambda": ["lambda"],
                "with": ["with "], "async def": ["async def"], "await": ["await"], "async with": ["async with"],
                "async for": ["async for"], "X | None": ["| None"]}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rastreados(base: Path, modulo: int | None = None) -> dict[str, str]:
    """caminho relativo -> hash, dos arquivos que a esteira protege."""
    achados: dict[str, str] = {}
    padroes = [f"modulo-{modulo:02d}/**/*"] if modulo is not None else ["modulo-*/**/*", "README.md", "ferramentas/imagens.json"]
    for pad in padroes:
        for p in base.glob(pad):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".md", ".py", ".json", ".png"):
                achados[str(p.relative_to(base))] = sha(p)
    return achados


def fences(linhas: list[str]) -> list[dict]:
    blocos, i = [], 0
    while i < len(linhas):
        m = FENCE_ABRE.match(linhas[i])
        if m and m.group(1):
            lang, ini, rotulo = m.group(1), i, None
            k = i - 1
            while k >= 0 and not linhas[k].strip():
                k -= 1
            if k >= 0 and ROTULO.match(linhas[k].strip()):
                rotulo = ROTULO.match(linhas[k].strip()).group(1)
            j = i + 1
            while j < len(linhas) and linhas[j].strip() != "```":
                j += 1
            blocos.append({"lang": lang, "ini": ini, "fim": j, "texto": "\n".join(linhas[i + 1:j]), "rotulo": rotulo})
            i = j
        elif m:
            j = i + 1
            while j < len(linhas) and linhas[j].strip() != "```":
                j += 1
            i = j
        i += 1
    return blocos


def termo_busca(chave: str) -> list[str]:
    if chave.startswith("py:"):
        return SINONIMOS_PY.get(chave[3:], [chave[3:]])
    m = re.match(r"^\w+\((\w+)=\)$", chave)
    if m:
        return [m.group(1)]
    return [chave.lstrip(".@").replace("[...]", "[")]


class Validacao:
    def __init__(self, cid: str, raiz: Path, original: Path, links_modulo0: bool):
        self.cid, self.raiz, self.original, self.links_modulo0 = cid, raiz, original, links_modulo0
        self.tarefa = json.loads((ESTEIRA / "tarefas" / f"{cid}.json").read_text())
        self.contrato = json.loads((ESTEIRA / "contrato.json").read_text())
        self.novo = self.tarefa["modulo"] == 0
        self.mod = f"modulo-{self.tarefa['modulo']:02d}"
        self.rel = self.tarefa["arquivo"]
        self.md = raiz / self.rel
        self.erros: list[tuple[str, str]] = []
        self.avisos: list[str] = []
        self.linhas = self.md.read_text().splitlines() if self.md.exists() else []
        orig_md = original / self.rel
        self.linhas_orig = orig_md.read_text().splitlines() if orig_md.exists() else []
        self.adicionadas: set[int] = set()
        self.passe2 = cid.endswith("p2")
        pref = cid.removesuffix("p2").replace(".", "-")
        self.prefixo_img = pref

    def erro(self, portao: str, msg: str) -> None:
        self.erros.append((portao, msg))

    # G1 — só adições
    def g1_aditivo(self) -> None:
        if not self.md.exists():
            return self.erro("G1", f"arquivo não existe: {self.rel}")
        if self.novo:
            if (self.original / self.rel).exists():
                self.erro("G1", "capítulo do Módulo 0 não deveria existir no original")
            self.adicionadas = set(range(len(self.linhas)))
            return
        sm = difflib.SequenceMatcher(a=self.linhas_orig, b=self.linhas, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "insert":
                self.adicionadas.update(range(j1, j2))
            elif tag in ("delete", "replace"):
                trecho = " / ".join(l[:60] for l in self.linhas_orig[i1:i2][:3])
                self.erro("G1", f"linha(s) original(is) alterada(s) ou removida(s) na linha {i1 + 1}: {trecho}")

    # G2 — nada colateral mudou no módulo
    def g2_colateral(self) -> None:
        base = rastreados(self.original, self.tarefa["modulo"] if not self.novo else None) if not self.novo else {}
        estado_arq = self.raiz / "ferramentas" / "esteira" / "estado.json"
        aceitos = json.loads(estado_arq.read_text()) if estado_arq.exists() else {}
        atual = rastreados(self.raiz, self.tarefa["modulo"])
        raiz_base = rastreados(self.original)
        for caminho, h in raiz_base.items():
            if caminho.startswith(f"{self.mod}/"):
                continue
            if caminho in ("README.md", "ferramentas/imagens.json") and (self.raiz / caminho).exists() and sha(self.raiz / caminho) != aceitos.get(caminho, h):
                self.erro("G2", f"arquivo compartilhado alterado: {caminho}")
        for caminho, h in base.items():
            esperado = aceitos.get(caminho, h)
            if caminho == self.rel:
                continue
            if caminho not in atual:
                self.erro("G2", f"arquivo removido: {caminho}")
            elif atual[caminho] != esperado:
                self.erro("G2", f"arquivo existente alterado fora do escopo: {caminho}")
        for caminho in atual:
            if caminho in base or caminho == self.rel or caminho in aceitos:
                continue
            if not (caminho.startswith(f"{self.mod}/codigo/") and caminho.endswith(".py")):
                if not (self.novo and caminho.startswith("modulo-00/")):
                    self.erro("G2", f"arquivo novo fora do permitido (só .py em codigo/): {caminho}")

    def novos_py(self) -> list[Path]:
        pasta = self.raiz / self.mod / "codigo"
        base = {Path(c).name for c in rastreados(self.original, self.tarefa["modulo"]) if "/codigo/" in c} if not self.novo else set()
        estado_arq = self.raiz / "ferramentas" / "esteira" / "estado.json"
        aceitos = json.loads(estado_arq.read_text()) if estado_arq.exists() else {}
        aceitos_nomes = {Path(c).name for c in aceitos if "/codigo/" in c}
        return sorted(p for p in pasta.glob("*.py") if p.name not in base and p.name not in aceitos_nomes) if pasta.exists() else []

    # G3 + G4 — código idêntico ao texto e executável offline com saída igual
    def g3_g4_codigo(self) -> None:
        blocos = fences(self.linhas)
        orig_blocos = {b["texto"].strip() for b in fences(self.linhas_orig)}
        rotulados = {b["rotulo"]: b for b in blocos if b["lang"] == "python" and b["rotulo"]}
        for rotulo, b in rotulados.items():
            arq = self.raiz / self.mod / "codigo" / rotulo
            if b["texto"].strip() in orig_blocos:
                continue
            if not arq.exists():
                self.erro("G3", f"bloco rotulado *{rotulo}* sem arquivo em codigo/")
            elif arq.read_text().strip() != b["texto"].strip():
                self.erro("G3", f"*{rotulo}*: o bloco do texto difere do arquivo em codigo/")
        for arq in self.novos_py():
            if arq.name not in rotulados:
                self.erro("G3", f"codigo/{arq.name} é novo mas não aparece no texto como bloco *{arq.name}*")
                continue
            env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", ""), "PYTHONDONTWRITEBYTECODE": "1",
                   "PYTHONIOENCODING": "utf-8", "LANG": "C.UTF-8"}
            try:
                r = subprocess.run([str(VENV_PY), arq.name], cwd=arq.parent, env=env, capture_output=True, text=True, timeout=90)
            except subprocess.TimeoutExpired:
                self.erro("G4", f"{arq.name}: excedeu 90 s (exemplos devem rodar offline e rápido)")
                continue
            if r.returncode != 0:
                self.erro("G4", f"{arq.name}: saiu com erro ({r.returncode}): {r.stderr.strip().splitlines()[-1:]} ")
                continue
            b = rotulados[arq.name]
            k = b["fim"] + 1
            while k < len(self.linhas) and (not self.linhas[k].strip() or not self.linhas[k].startswith("```")) and k < b["fim"] + 5:
                k += 1
            if k < len(self.linhas) and self.linhas[k].strip() == "```text":
                j = k + 1
                while j < len(self.linhas) and self.linhas[j].strip() != "```":
                    j += 1
                esperado = [l.rstrip() for l in self.linhas[k + 1:j]]
                obtido = [l.rstrip() for l in r.stdout.rstrip("\n").splitlines()]
                if esperado != obtido:
                    dif = list(difflib.unified_diff(esperado, obtido, "texto", "execução", lineterm="", n=0))[:6]
                    self.erro("G4", f"{arq.name}: a saída mostrada no texto difere da real:\n      " + "\n      ".join(dif))
            else:
                self.avisos.append(f"{arq.name}: sem bloco ```text de saída logo abaixo (recomendado)")

    # G5 — sintaxe e fences
    def g5_sintaxe(self) -> None:
        if sum(1 for l in self.linhas if l.strip().startswith("```")) % 2:
            self.erro("G5", "número ímpar de cercas ``` (bloco de código não fechado)")
        orig_blocos = {b["texto"].strip() for b in fences(self.linhas_orig)}
        for b in fences(self.linhas):
            if b["lang"] == "python" and b["texto"].strip() not in orig_blocos:
                try:
                    ast.parse(b["texto"])
                except SyntaxError as e:
                    self.erro("G5", f"bloco python (linha {b['ini'] + 1}) não compila: {e.msg} (linha {e.lineno})")

    # G6 — estrutura, formatos e links
    def g6_estrutura(self) -> None:
        txt = "\n".join(self.linhas)
        if txt.count("\n## Recapitulando") != 1:
            self.erro("G6", "o capítulo precisa ter exatamente um '## Recapitulando'")
        if txt.count("\n### Fontes do capítulo") != 1:
            self.erro("G6", "o capítulo precisa ter exatamente um '### Fontes do capítulo'")
        novas = [self.linhas[i] for i in sorted(self.adicionadas)]
        titulos = [l for l in novas if re.match(r"^#{2,4} ", l)]
        if len(titulos) != len(set(titulos)):
            self.erro("G6", "títulos duplicados entre as linhas adicionadas")
        for l in novas:
            if l.startswith("> **Por dentro do PydanticAI"):
                if not re.match(r"^> \*\*Por dentro do PydanticAI — `[^`]+`\*\*$", l):
                    self.erro("G6", f"cabeçalho de caixa fora do formato: {l[:80]}")
        palavras = sum(len(l.split()) for i, l in enumerate(self.linhas) if i in self.adicionadas)
        if self.novo:
            if not (1600 <= palavras <= 4200):
                self.erro("G6", f"capítulo novo com {palavras} palavras (esperado 2.000 a 3.000; limites 1.600 a 4.200)")
            if not self.linhas or not self.linhas[0].startswith(f"# Capítulo {self.cid} — "):
                self.erro("G6", f"o título deve começar com '# Capítulo {self.cid} — '")
            if txt.count("### Faça você mesmo") < 2:
                self.erro("G6", "o capítulo novo precisa de pelo menos 2 blocos '### Faça você mesmo'")
        elif self.passe2:
            anat = [l for l in novas if l.startswith("> **Anatomia do código")]
            for l in anat:
                if not re.match(r"^> \*\*Anatomia do código — `[^`]+`\*\*$", l):
                    self.erro("G6", f"cabeçalho de caixa fora do formato '> **Anatomia do código — `arquivo.py`**': {l[:80]}")
            if not 1 <= len(anat) <= 3:
                self.erro("G6", f"o passe 2 deve acrescentar de 1 a 3 caixas 'Anatomia do código' (há {len(anat)})")
            if any(l.startswith("> **Antes de começar") for l in novas):
                self.erro("G6", "a caixa 'Antes de começar' é do passe 1; não a repita")
            if palavras > 1200:
                self.erro("G6", f"{palavras} palavras adicionadas no passe 2 (máximo 1.200; meta ~500)")
            elif palavras > 800:
                self.avisos.append(f"{palavras} palavras adicionadas no passe 2 (meta ~500)")
        else:
            antes = [l for l in novas if l.startswith("> **Antes de começar — PydanticAI neste capítulo**")]
            if len(antes) != 1:
                self.erro("G6", "falta (ou há mais de uma) caixa '> **Antes de começar — PydanticAI neste capítulo**'")
            if palavras > 1500:
                self.erro("G6", f"{palavras} palavras adicionadas (máximo 1.500; meta ~900)")
            elif palavras > 1100:
                self.avisos.append(f"{palavras} palavras adicionadas (meta ~900)")
        arqs_m0 = {Path(c["arquivo"]).name for c in self.contrato["modulo0"]}
        for l in novas if not self.novo else self.linhas:
            for alvo in re.findall(r"\]\(\.\./modulo-00/([^)#]+)\)", l):
                if alvo not in arqs_m0:
                    self.erro("G6", f"link para capítulo inexistente do Módulo 0: {alvo}")
            for n in re.findall(r"Capítulo 0\.(\d+)", l):
                if f"0.{n}" not in {c["id"] for c in self.contrato["modulo0"]}:
                    self.erro("G6", f"referência a Capítulo 0.{n} que não existe no contrato")
        for l in (novas if not self.novo else self.linhas):
            if EMOJI.search(l):
                self.erro("G8", f"emoji não permitido: {l[:60]}")
            if re.search(r"\b(TODO|FIXME|lorem ipsum)\b", l, re.I):
                self.erro("G8", f"marcador de rascunho: {l[:60]}")

    # G7 — imagens
    def g7_imagens(self) -> None:
        frag = self.raiz / "ferramentas" / "esteira" / "imagens" / f"{self.cid}.json"
        entradas = []
        if frag.exists():
            try:
                entradas = json.loads(frag.read_text())
            except json.JSONDecodeError as e:
                return self.erro("G7", f"{frag.name} não é JSON válido: {e}")
        limite = 4 if self.novo else 2
        if len(entradas) > limite:
            self.erro("G7", f"{len(entradas)} imagens propostas (máximo {limite})")
        nomes = set()
        manifesto = json.loads((self.original / "ferramentas" / "imagens.json").read_text())["imagens"] if (self.original / "ferramentas" / "imagens.json").exists() else []
        existentes = {m["arquivo"] for m in manifesto}
        for e in entradas:
            arq, prompt = e.get("arquivo", ""), e.get("prompt", "")
            if not re.match(rf"^{re.escape(self.mod)}/img/cap{re.escape(self.prefixo_img)}-[a-z0-9-]+\.png$", arq):
                self.erro("G7", f"nome de imagem fora do padrão {self.mod}/img/cap{self.prefixo_img}-<slug>.png: {arq}")
            if arq in nomes or arq in existentes or (self.raiz / arq).exists():
                self.erro("G7", f"imagem já existente ou repetida: {arq}")
            nomes.add(arq)
            if not (80 <= len(prompt) <= 1400):
                self.erro("G7", f"prompt de {arq} com {len(prompt)} caracteres (esperado 80 a 1.400)")
        refs = re.findall(r"!\[([^\]]*)\]\((img/[^)]+\.png)\)", "\n".join(self.linhas[i] for i in sorted(self.adicionadas)))
        for alt, caminho in refs:
            completo = f"{self.mod}/{caminho}"
            if not alt.strip():
                self.erro("G7", f"imagem sem texto alternativo: {caminho}")
            if completo not in nomes and not (self.raiz / completo).exists():
                self.erro("G7", f"imagem referenciada não existe nem foi proposta: {caminho}")
        referenciadas = {f"{self.mod}/{c}" for _, c in refs}
        for n in nomes:
            if n not in referenciadas:
                self.erro("G7", f"imagem proposta mas não inserida no capítulo: {n}")

    # G9/G10 — relatório e cobertura de símbolos
    def g9_relatorio(self) -> None:
        pasta = self.raiz / "ferramentas" / "esteira" / "relatorios"
        rmd, rjs = pasta / f"{self.cid}.md", pasta / f"{self.cid}.json"
        if not rmd.exists() or not rjs.exists():
            return self.erro("G9", f"faltam os relatórios {rmd.name} e/ou {rjs.name} em ferramentas/esteira/relatorios/")
        titulos = re.findall(r"^## (.+)$", rmd.read_text(), flags=re.M)
        for s in SECOES_RELATORIO:
            if s not in titulos:
                self.erro("G10", f"relatório sem a seção '## {s}'")
        try:
            rel = json.loads(rjs.read_text())
        except json.JSONDecodeError as e:
            return self.erro("G9", f"{rjs.name} inválido: {e}")
        regs = {s.get("chave"): s for s in rel.get("simbolos", [])}
        novas = "\n".join(self.linhas[i] for i in sorted(self.adicionadas))
        caixas = [l for l in novas.splitlines() if l.startswith("> **Por dentro do PydanticAI")]
        for chave in self.tarefa["explicar_aqui"]:
            reg = regs.get(chave)
            if not reg:
                self.erro("G9", f"símbolo '{chave}' não consta no relatório JSON")
                continue
            if self.novo:
                if not any(t in "\n".join(self.linhas) for t in termo_busca(chave)):
                    self.erro("G9", f"o capítulo (dono) não menciona '{chave}' (procurado: {termo_busca(chave)})")
            elif reg.get("status") != "explicado_aqui":
                self.erro("G9", f"símbolo obrigatório '{chave}' deve ter status 'explicado_aqui'")
            elif not any(any(t in c for t in termo_busca(chave)) for c in caixas):
                self.erro("G9", f"falta a caixa '> **Por dentro do PydanticAI — `...`**' para '{chave}'")
        if not self.novo:
            for chave in self.tarefa["apontar"]:
                if chave not in regs:
                    self.erro("G9", f"símbolo '{chave}' (Módulo 0) não consta no relatório JSON")
            antes = [l for l in novas.splitlines() if l.startswith("> ") or l.startswith(">")]
            texto_antes = "\n".join(antes)
            for dono in self.tarefa["donos_modulo0"]:
                if f"0.{dono[2:]}" not in texto_antes and f"Capítulo {dono}" not in texto_antes:
                    self.erro("G9", f"a caixa 'Antes de começar' não aponta para o Capítulo {dono}")
        if "correcoes_sugeridas" not in rel:
            self.erro("G9", "o JSON do relatório precisa do campo 'correcoes_sugeridas' (pode ser lista vazia)")

    # G11 — nomes citados existem de verdade
    def g11_nomes(self) -> None:
        texto = "\n".join(self.linhas[i] for i in sorted(self.adicionadas))
        alvos = sorted({m for m in re.findall(r"`((?:pydantic_ai|pydantic|pydantic_evals|pydantic_graph)(?:\.\w+)+)`", texto)})
        if not alvos:
            return
        script = ("import importlib,json,sys\n"
                  "ruins=[]\n"
                  "for nome in json.loads(sys.argv[1]):\n"
                  "    partes=nome.split('.');obj=None\n"
                  "    for i in range(len(partes),0,-1):\n"
                  "        try: obj=importlib.import_module('.'.join(partes[:i]));resto=partes[i:];break\n"
                  "        except Exception: continue\n"
                  "    else: ruins.append(nome);continue\n"
                  "    try:\n"
                  "        for r in resto: obj=getattr(obj,r)\n"
                  "    except AttributeError: ruins.append(nome)\n"
                  "print(json.dumps(ruins))\n")
        r = subprocess.run([str(VENV_PY), "-c", script, json.dumps(alvos)], capture_output=True, text=True, timeout=60)
        try:
            ruins = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return self.avisos.append("não consegui resolver os nomes citados (G11)")
        for n in ruins:
            self.erro("G11", f"o nome `{n}` citado no texto não existe na versão instalada")

    def rodar(self) -> bool:
        self.g1_aditivo()
        if self.md.exists():
            self.g2_colateral()
            self.g3_g4_codigo()
            self.g5_sintaxe()
            self.g6_estrutura()
            self.g7_imagens()
            self.g9_relatorio()
            self.g11_nomes()
        return not self.erros


def aceitar(v: Validacao) -> None:
    import fcntl
    arq = v.raiz / "ferramentas" / "esteira" / "estado.json"
    arq.parent.mkdir(parents=True, exist_ok=True)
    with open(arq.with_suffix(".lock"), "w") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        estado = json.loads(arq.read_text()) if arq.exists() else {}
        estado.update(rastreados(v.raiz, v.tarefa["modulo"]))
        arq.write_text(json.dumps(estado, indent=1, sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--raiz", default=str(LIVRO))
    ap.add_argument("--original", default=str(ORIGINAL))
    ap.add_argument("--aceitar", action="store_true")
    ap.add_argument("--sem-links-modulo0", action="store_true")
    a = ap.parse_args()
    original = Path(a.original)
    if a.id.endswith("p2") and a.original == str(ORIGINAL):
        original = PROJETO / "scratch" / "livro-passe1"  # passe 2 protege também o que o passe 1 acrescentou
    v = Validacao(a.id, Path(a.raiz), original, not a.sem_links_modulo0)
    ok = v.rodar()
    portoes = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11"]
    for p in portoes:
        falhas = [m for q, m in v.erros if q == p]
        if falhas:
            print(f"[{p}] FALHOU")
            for m in falhas[:6]:
                print(f"   - {m}")
    for av in v.avisos:
        print(f"[aviso] {av}")
    resumo = {"id": a.id, "aprovado": ok, "erros": v.erros, "avisos": v.avisos,
              "palavras_adicionadas": sum(len(l.split()) for i, l in enumerate(v.linhas) if i in v.adicionadas)}
    destino = Path(a.raiz) / "ferramentas" / "esteira" / "relatorios"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / f"{a.id}.validacao.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1))
    if ok and a.aceitar:
        aceitar(v)
    print(f"{'APROVADO' if ok else 'REPROVADO'} ({len(v.erros)} erro(s), {resumo['palavras_adicionadas']} palavras adicionadas)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
