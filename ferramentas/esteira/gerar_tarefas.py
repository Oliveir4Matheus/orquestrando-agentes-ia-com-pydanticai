"""Gera as tarefas por capítulo (tarefas/<id>.md e .json) a partir do mapa e do contrato.

Uso: python3 gerar_tarefas.py [--raiz DIR]   (DIR = onde o worker vai escrever; padrão: o livro)
"""
import json
import sys
from pathlib import Path

ESTEIRA = Path(__file__).resolve().parent
LIVRO = ESTEIRA.parent.parent
PROJETO = LIVRO.parent
VENV_PY = PROJETO / ".venv" / "bin" / "python"


def carregar():
    mapa = json.loads((ESTEIRA / "mapa.json").read_text())
    contrato = json.loads((ESTEIRA / "contrato.json").read_text())
    donos: dict[str, str] = {}
    for cap in contrato["modulo0"]:
        for s in cap["simbolos"]:
            donos.setdefault(s, cap["id"])
    return mapa, contrato, donos


def dono_de(simbolo: dict, donos: dict[str, str]) -> str | None:
    return donos.get(simbolo["chave"]) or donos.get(simbolo["nome"])


def imagens_do_modulo(modulo: int) -> list[str]:
    pasta = LIVRO / f"modulo-{modulo:02d}" / "img"
    return sorted(p.name for p in pasta.glob("*.png")) if pasta.exists() else []


def tabela_modulo0(contrato: dict) -> str:
    linhas = ["| Cap. | Título | Arquivo (link relativo a partir de `modulo-NN/`) |", "| --- | --- | --- |"]
    for c in contrato["modulo0"]:
        nome = Path(c["arquivo"]).name
        linhas.append(f"| 0.{c['id'][2:]} | {c['titulo']} | `../modulo-00/{nome}` |")
    return "\n".join(linhas)


def gerar_capitulo(cap: dict, mapa: dict, contrato: dict, donos: dict[str, str], raiz: Path) -> None:
    obrigatorios, apontar = [], []
    for s in cap["simbolos_novos"]:
        d = dono_de(s, donos)
        (apontar if d else obrigatorios).append({**s, "dono": d})
    cid = cap["id"]
    dados = {"id": cid, "arquivo": cap["arquivo"], "modulo": cap["modulo"], "raiz": str(raiz),
             "explicar_aqui": [s["chave"] for s in obrigatorios],
             "apontar": {s["chave"]: s["dono"] for s in apontar},
             "donos_modulo0": sorted({s["dono"] for s in apontar})}
    (ESTEIRA / "tarefas" / f"{cid}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1))

    def linhas(itens, com_dono):
        if not itens:
            return "_(nenhum)_"
        cab = "| Símbolo | Tipo | Citado no texto? |" + (" Dono |" if com_dono else "")
        sep = "| --- | --- | --- |" + (" --- |" if com_dono else "")
        corpo = [f"| `{s['chave']}` | {s['tipo']} | {'sim' if s['mencionado_no_texto'] else 'não (só no código)'} |"
                 + (f" Capítulo {s['dono']} |" if com_dono else "") for s in itens]
        return "\n".join([cab, sep, *corpo])

    existentes = ", ".join(imagens_do_modulo(cap["modulo"])) or "(nenhuma)"
    cmd = f"python3 {ESTEIRA}/validar.py {cid} --raiz {raiz}"
    md = f"""# Tarefa — Capítulo {cid} (`{cap['arquivo']}`)

Leia primeiro `{ESTEIRA}/padrao.md` (regras, formatos, relatório). Depois execute esta tarefa.

**Raiz de trabalho:** `{raiz}` — todos os caminhos relativos abaixo são relativos a ela.
**Capítulo:** `{cap['arquivo']}` ({cap['palavras']} palavras). Código do módulo: `modulo-{cap['modulo']:02d}/codigo/`.
**Imagens já existentes no módulo (não repita):** {existentes}.

## Símbolos que ESTE capítulo usa pela primeira vez e que NINGUÉM mais ensina → explique (caixa “Por dentro do PydanticAI”, uma por símbolo)

{linhas(obrigatorios, False)}

## Símbolos ensinados no Módulo 0 → só aponte (caixa “Antes de começar” + lembrete curto se o uso não for óbvio)

{linhas(apontar, True)}

Capítulos do Módulo 0 (os links devem apontar para estes arquivos):

{tabela_modulo0(contrato)}

## Além da lista

A lista acima vem de uma varredura automática do código. Use seu julgamento: se um iniciante travaria em outro ponto de Python, Pydantic ou PydanticAI deste capítulo (um argumento, um tipo, uma saída), acrescente a explicação também e registre no relatório.

## Entregáveis e validação

- Capítulo editado só por inserções; código novo em `modulo-{cap['modulo']:02d}/codigo/` (offline); relatório `ferramentas/esteira/relatorios/{cid}.md` e `.json`; imagens (0 a 2) em `ferramentas/esteira/imagens/{cid}.json`.
- Valide com: `{cmd}` — até aparecer `APROVADO`.
"""
    (ESTEIRA / "tarefas" / f"{cid}.md").write_text(md)


def gerar_modulo0(contrato: dict, raiz: Path) -> None:
    for c in contrato["modulo0"]:
        cid = c["id"]
        dados = {"id": cid, "arquivo": c["arquivo"], "modulo": 0, "raiz": str(raiz), "explicar_aqui": c["simbolos"],
                 "apontar": {}, "donos_modulo0": []}
        (ESTEIRA / "tarefas" / f"{cid}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1))
        cmd = f"python3 {ESTEIRA}/validar.py {cid} --raiz {raiz}"
        md = f"""# Tarefa — Capítulo {cid} do Módulo 0 (novo): {c['titulo']}

Leia primeiro `{ESTEIRA}/padrao.md` e `{LIVRO}/modulo-01/02-modelo-ferramentas-instrucoes.md` (para absorver a voz e o formato). **Este capítulo é novo**: você o escreve inteiro em `{c['arquivo']}`.

**Raiz de trabalho:** `{raiz}` — todos os caminhos relativos abaixo são relativos a ela.

**Conteúdo:** {c['resumo']}

**Símbolos de que este capítulo é DONO** (explique cada um por completo, com exemplo executável, nome do símbolo em crases): {', '.join(f'`{s}`' for s in c['simbolos'])}

**Estrutura obrigatória** (modelo do livro): `# Capítulo {cid} — {c['titulo']}`; introdução que liga ao capítulo anterior; 1 imagem de abertura; seções `##` em degraus pequenos (necessidade concreta → exemplo mínimo → resultado → explicação → variação → armadilha → exercício); `### Faça você mesmo` (exercícios {cid}.1, {cid}.2...) ao fim de cada unidade; `## Recapitulando` com ponte para o próximo; `### Fontes do capítulo` (documentação do PydanticAI/Pydantic realmente consultada, com links). Tamanho: 2.000 a 3.000 palavras. Capítulos do Módulo 0:

{tabela_modulo0(contrato)}

Todos os exemplos rodam **offline** (Pydantic puro, `TestModel` ou `FunctionModel`) e ficam em `modulo-00/codigo/`, idênticos ao texto, com a saída real mostrada. Imagens: 2 a 3, em `ferramentas/esteira/imagens/{cid}.json`. Relatório: `ferramentas/esteira/relatorios/{cid}.md` e `.json` (seções do padrão; `Inventário` lista o que o capítulo cobre).

Valide com: `{cmd}` — até aparecer `APROVADO`.
"""
        (ESTEIRA / "tarefas" / f"{cid}.md").write_text(md)


def main() -> None:
    raiz = Path(sys.argv[sys.argv.index("--raiz") + 1]) if "--raiz" in sys.argv else LIVRO
    mapa, contrato, donos = carregar()
    for cap in mapa["capitulos"]:
        gerar_capitulo(cap, mapa, contrato, donos, raiz)
    gerar_modulo0(contrato, raiz)
    print(f"{len(mapa['capitulos'])} tarefas de capítulo + {len(contrato['modulo0'])} do Módulo 0 em {ESTEIRA / 'tarefas'}")


if __name__ == "__main__":
    main()
