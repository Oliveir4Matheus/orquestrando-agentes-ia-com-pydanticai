"""Gera as tarefas do PASSE 2 (tarefas/<id>p2.md e .json): anotar, no contexto, o código central de cada capítulo.

Uso: python3 gerar_passe2.py [--raiz DIR]
"""
import ast
import json
import re
import sys
from pathlib import Path

from validar import fences  # noqa: E402

ESTEIRA = Path(__file__).resolve().parent
LIVRO = ESTEIRA.parent.parent
PACOTES = ("pydantic_ai", "pydantic", "pydantic_evals", "pydantic_graph", "logfire", "fastmcp", "mcp")
METODOS = {"run", "run_sync", "run_stream", "iter", "override", "tool", "tool_plain", "instructions", "output_validator",
           "model_validate", "model_validate_json", "model_dump", "model_dump_json", "model_json_schema", "all_messages",
           "new_messages", "gather", "create_task", "evaluate", "evaluate_sync", "add_case", "stream_text", "stream_output"}
ATRIBUTOS = {"output", "usage", "deps", "retry", "requests", "tool_calls", "parts", "content", "tool_name", "args", "tool_call_id"}


def elementos(codigo: str) -> list[str]:
    try:
        arv = ast.parse(codigo)
    except SyntaxError:
        return []
    importados = set()
    achados: set[str] = set()
    for no in ast.walk(arv):
        if isinstance(no, ast.ImportFrom) and no.module and no.module.split(".")[0] in PACOTES:
            importados.update(a.asname or a.name for a in no.names)
    for no in ast.walk(arv):
        if isinstance(no, ast.Call):
            f = no.func
            nome = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            ehmetodo = isinstance(f, ast.Attribute) and f.attr in METODOS
            if nome in importados or ehmetodo:
                kws = [k.arg for k in no.keywords if k.arg]
                achados.add(f"{'.' if ehmetodo else ''}{nome}({', '.join(k + '=' for k in kws)})" if kws else f"{'.' if ehmetodo else ''}{nome}()")
        if isinstance(no, ast.Attribute) and no.attr in ATRIBUTOS:
            base = no.value.id if isinstance(no.value, ast.Name) else "…"
            achados.add(f"{base}.{no.attr}")
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in no.decorator_list:
                b = d.func if isinstance(d, ast.Call) else d
                if isinstance(b, ast.Attribute) and b.attr in METODOS:
                    achados.add(f"@{ast.unparse(b)}")
    return sorted(achados)


def gerar(cap: dict, contrato: dict, raiz: Path) -> None:
    cid = cap["id"]
    arq = raiz / cap["arquivo"]
    linhas = arq.read_text().splitlines()
    blocos = []
    for b in fences(linhas):
        if b["lang"] == "python":
            el = elementos(b["texto"])
            if el:
                blocos.append({"rotulo": b["rotulo"] or f"(bloco sem rótulo, linha {b['ini'] + 1})", "linha": b["ini"] + 1, "elementos": el})
    blocos.sort(key=lambda b: -len(b["elementos"]))
    cand = sorted(blocos[:4], key=lambda b: b["linha"])
    tabela = "\n".join(f"| `{b['rotulo']}` | {b['linha']} | " + ", ".join(f"`{e}`" for e in b["elementos"][:14]) + " |" for b in cand) or "| (nenhum bloco usa o PydanticAI) | | |"
    imgs = ", ".join(sorted(p.name for p in (raiz / f"modulo-{cap['modulo']:02d}" / "img").glob("*.png"))) or "(nenhuma)"
    md0 = "\n".join(f"- Capítulo {c['id']}: {c['titulo']} (`../modulo-00/{Path(c['arquivo']).name}`)" for c in contrato["modulo0"])
    texto = f"""# Tarefa (PASSE 2) — Capítulo {cid} (`{cap['arquivo']}`): ler o código do capítulo, no contexto

Leia primeiro `{ESTEIRA}/padrao.md` (regras gerais, relatório, validação). **Neste passe, ignore as seções 3A e 3B do padrão** (caixas “Antes de começar” e “Por dentro”): elas foram feitas no passe 1 e **não devem ser alteradas**. Siga o formato abaixo.

**Raiz de trabalho:** `{raiz}` — caminhos relativos são relativos a ela. Capítulo: `{cap['arquivo']}`; código: `modulo-{cap['modulo']:02d}/codigo/`.
**Imagens já existentes no módulo (não repita):** {imgs}.

## O problema que este passe resolve

O aluno chega ao código do capítulo e vê chamadas do PydanticAI/Pydantic (métodos, argumentos, atributos do resultado) sem que ninguém diga **o que cada uma faz neste exemplo**. As definições gerais estão no Módulo 0; falta a leitura **em contexto**. Seu trabalho: acrescentar, depois do parágrafo que comenta cada bloco central, uma caixa que **lê o código passo a passo**.

## Blocos candidatos (escolha de 1 a 3, os mais ricos em PydanticAI e mais úteis ao entendimento)

| Bloco | Linha | Elementos detectados (automático) |
| --- | --- | --- |
{tabela}

## Formato obrigatório (1 a 3 caixas; cada uma até ~220 palavras; total até ~600)

```
> **Anatomia do código — `arquivo.py`**
>
> 1. **`agente.run(pergunta, usage=ctx.usage)`** — chama o outro agente e **soma** o consumo dele ao do agente atual; sem `usage=`, o limite de requisições deixaria de enxergar essa chamada.
> 2. **`ctx.deps`** — ...
```

Regras:
- Cada item: o elemento em negrito e crases, travessão e 1 a 2 frases que digam **o que ele faz, o que recebe, o que devolve e por que está aqui**, com os nomes do exemplo. Siga a ordem do código.
- Só o que é do PydanticAI/Pydantic (e async/await quando for o ponto). Não explique Python trivial, nem repita o que a caixa “Por dentro” do passe 1 já explicou, nem o enredo de orquestração do capítulo.
- Quando a definição geral estiver no Módulo 0, aponte em vez de repetir (formato do link: `[Capítulo 0.N](../modulo-00/<arquivo>.md)`):
{md0}
- **Confira cada afirmação**: leia a doc (`{LIVRO.parent}/docs/`) e rode um teste no venv (`{LIVRO.parent}/.venv/bin/python`). Se um elemento se comportar de modo surpreendente, é isso que mais vale registrar.
- A caixa vai **logo depois do parágrafo que comenta o bloco** (e da saída, se houver), nunca dentro de código, tabela ou lista. Nada do texto existente muda.
- Código novo só se for indispensável (offline, rótulo `*nome.py*`, saída real) — normalmente não é.

## Imagem (recomendada: 1)

Proponha **uma** imagem que mostre o mecanismo do PydanticAI que o código do capítulo usa e que é difícil de enxergar lendo o código (ex.: o caminho da mensagem entre agente e ferramenta, a injeção de `deps`, a propagação de `usage`, a repetição por validação, o ciclo de mensagens). Não repita as existentes nem o diagrama de orquestração do capítulo. Escreva em `ferramentas/esteira/imagens/{cid}p2.json` (formato do padrão, seção 6) e insira `![descrição](img/capN-slug.png)` com uma frase de apresentação. Nome: `modulo-{cap['modulo']:02d}/img/cap{cid}-<slug>.png`. Se nenhuma imagem acrescentar entendimento, não force: registre o motivo no relatório.

## Entregáveis

Capítulo editado só por inserções; relatório `ferramentas/esteira/relatorios/{cid}p2.md` e `.json` (mesmas seções do padrão; em `Inventário`, liste os elementos que você anotou e os que deixou de fora, com o motivo); imagem (0 ou 1). Valide com: `python3 {ESTEIRA}/validar.py {cid}p2 --raiz {raiz}` até aparecer `APROVADO`.
"""
    (ESTEIRA / "tarefas" / f"{cid}p2.md").write_text(texto)
    (ESTEIRA / "tarefas" / f"{cid}p2.json").write_text(json.dumps(
        {"id": f"{cid}p2", "arquivo": cap["arquivo"], "modulo": cap["modulo"], "raiz": str(raiz),
         "explicar_aqui": [], "apontar": {}, "donos_modulo0": [], "blocos_candidatos": cand}, ensure_ascii=False, indent=1))


def main() -> None:
    raiz = Path(sys.argv[sys.argv.index("--raiz") + 1]) if "--raiz" in sys.argv else LIVRO
    mapa = json.loads((ESTEIRA / "mapa.json").read_text())
    contrato = json.loads((ESTEIRA / "contrato.json").read_text())
    for cap in mapa["capitulos"]:
        gerar(cap, contrato, raiz)
    print(f"{len(mapa['capitulos'])} tarefas de passe 2 em {ESTEIRA / 'tarefas'}")


if __name__ == "__main__":
    main()
