"""Mapa de conceitos: onde cada símbolo do Pydantic/PydanticAI aparece pela primeira vez.

Lê os blocos ```python de cada capítulo (na ordem do livro), extrai os símbolos
das bibliotecas do ecossistema e dos conceitos de Python que o livro assume, e
grava `mapa.json`. Uso: python mapa_conceitos.py [--raiz DIR]
"""
import ast
import json
import re
import sys
from pathlib import Path

ESTEIRA = Path(__file__).resolve().parent
RAIZ = ESTEIRA.parent.parent
PACOTES = ("pydantic_ai", "pydantic", "pydantic_evals", "pydantic_graph", "logfire", "fastmcp", "mcp")
ATRIBUTOS = {
    "run", "run_sync", "run_stream", "iter", "override", "tool", "tool_plain", "instructions",
    "system_prompt", "output_validator", "usage", "output", "all_messages", "new_messages",
    "deps", "retry", "model_dump", "model_dump_json", "model_validate", "model_validate_json",
    "model_json_schema", "model_copy", "parts", "part_kind", "tool_name", "tool_call_id", "args",
    "args_as_dict", "content", "stream_text", "stream_output", "get_output", "requests",
    "tool_calls", "input_tokens", "output_tokens", "total_tokens", "validate_python",
    "validate_json", "dump_python", "dump_json", "function_tools", "output_tools",
}
CONCEITOS_PY = {
    ast.AsyncFunctionDef: "py:async def", ast.Await: "py:await", ast.AsyncWith: "py:async with",
    ast.AsyncFor: "py:async for", ast.With: "py:with", ast.Lambda: "py:lambda",
}
FENCE = re.compile(r"^```(\w*)\s*$")


def blocos_python(texto: str) -> list[str]:
    blocos, atual, dentro = [], [], False
    for linha in texto.splitlines():
        m = FENCE.match(linha)
        if m and not dentro and m.group(1) == "python":
            dentro, atual = True, []
        elif linha.strip() == "```" and dentro:
            blocos.append("\n".join(atual))
            dentro = False
        elif dentro:
            atual.append(linha)
    return blocos


def prosa(texto: str) -> str:
    return re.sub(r"```.*?```", "", texto, flags=re.S)


def simbolos_do_bloco(codigo: str) -> dict[str, tuple[str, str]]:
    """chave -> (nome, tipo)"""
    try:
        arvore = ast.parse(codigo)
    except SyntaxError:
        return {}
    achados: dict[str, tuple[str, str]] = {}
    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module and no.module.split(".")[0] in PACOTES:
            for alias in no.names:
                importados.add(alias.asname or alias.name)
                achados[alias.name] = (alias.name, "importação")
        elif isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.split(".")[0] in PACOTES:
                    importados.add(alias.asname or alias.name)
                    achados[alias.name] = (alias.name, "importação")
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call):
            alvo = no.func
            nome = alvo.id if isinstance(alvo, ast.Name) else None
            if nome in importados:
                for kw in no.keywords:
                    if kw.arg:
                        achados[f"{nome}({kw.arg}=)"] = (kw.arg, "argumento")
        if isinstance(no, ast.Attribute) and no.attr in ATRIBUTOS:
            achados[f".{no.attr}"] = (no.attr, "atributo/método")
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for dec in no.decorator_list:
                base = dec.func if isinstance(dec, ast.Call) else dec
                nome_dec = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", None)
                if nome_dec:
                    achados[f"@{nome_dec}"] = (nome_dec, "decorador")
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(no):
                achados["py:docstring"] = ("docstring", "python")
        if type(no) in CONCEITOS_PY:
            chave = CONCEITOS_PY[type(no)]
            achados[chave] = (chave.removeprefix("py:"), "python")
        if isinstance(no, ast.BinOp) and isinstance(no.op, ast.BitOr):
            lados = (no.left, no.right)
            if any(isinstance(x, ast.Constant) and x.value is None for x in lados):
                achados["py:X | None"] = ("X | None", "python")
        if isinstance(no, ast.Subscript) and isinstance(no.value, ast.Name) and no.value.id in ("Literal", "Annotated", "Union", "Optional"):
            achados[no.value.id] = (no.value.id, "python")
        if isinstance(no, ast.Subscript) and isinstance(no.value, ast.Name) and no.value.id in ("RunContext", "Agent"):
            achados[f"{no.value.id}[...]"] = (f"{no.value.id}[", "genérico")
        if isinstance(no, ast.AnnAssign) and isinstance(no.annotation, ast.Name) and no.annotation.id:
            achados["py:anotação de tipo"] = ("anotação", "python")
    return achados


def capitulos(raiz: Path) -> list[tuple[str, Path]]:
    itens = []
    for arq in sorted(raiz.glob("modulo-[0-9][0-9]/[0-9][0-9]-*.md")):
        if arq.name.startswith("00-"):
            continue
        itens.append((str(int(arq.name[:2])), arq))
    return sorted(itens, key=lambda x: int(x[0]))


def main() -> None:
    raiz = Path(sys.argv[sys.argv.index("--raiz") + 1]) if "--raiz" in sys.argv else RAIZ
    primeira: dict[str, str] = {}
    saida = []
    for cid, arq in capitulos(raiz):
        texto = arq.read_text()
        no_texto = prosa(texto)
        todos: dict[str, tuple[str, str]] = {}
        for bloco in blocos_python(texto):
            todos.update(simbolos_do_bloco(bloco))
        novos, reusados = [], []
        for chave, (nome, tipo) in sorted(todos.items()):
            if chave in primeira:
                reusados.append({"chave": chave, "primeira_vez": primeira[chave]})
                continue
            primeira[chave] = cid
            citado = bool(re.search(r"`[^`\n]*" + re.escape(nome.strip("[")) + r"[^`\n]*`", no_texto))
            novos.append({"chave": chave, "nome": nome, "tipo": tipo, "mencionado_no_texto": citado})
        saida.append({
            "id": cid, "modulo": int(arq.parent.name[-2:]), "arquivo": str(arq.relative_to(raiz)),
            "palavras": len(texto.split()), "simbolos_novos": novos, "simbolos_reusados": reusados,
        })
    (ESTEIRA / "mapa.json").write_text(json.dumps({"capitulos": saida, "primeira_vez": primeira}, ensure_ascii=False, indent=1))
    total = sum(len(c["simbolos_novos"]) for c in saida)
    sem_texto = sum(1 for c in saida for s in c["simbolos_novos"] if not s["mencionado_no_texto"])
    print(f"{len(saida)} capítulos, {total} símbolos distintos, {sem_texto} só aparecem no código (sem menção no texto).")


if __name__ == "__main__":
    main()
