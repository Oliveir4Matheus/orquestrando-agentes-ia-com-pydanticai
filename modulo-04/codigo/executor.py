import ast
import builtins
import io
import sys
from collections.abc import Callable
from contextlib import redirect_stdout

NOS_PERMITIDOS = (
    ast.Module, ast.Expr, ast.Assign, ast.AugAssign, ast.For, ast.While, ast.If,
    ast.Break, ast.Continue, ast.Pass,
    ast.Name, ast.Load, ast.Store, ast.Constant, ast.List, ast.Tuple, ast.Dict, ast.Set,
    ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Call, ast.keyword,
    ast.Attribute, ast.Subscript, ast.Slice,
    ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp, ast.comprehension,
    ast.JoinedStr, ast.FormattedValue,
    ast.operator, ast.unaryop, ast.boolop, ast.cmpop,
)
NOMES_SEGUROS = [
    "len", "sum", "min", "max", "sorted", "range", "print", "str", "int", "float",
    "round", "enumerate", "zip", "list", "dict", "set", "abs", "bool",
]
METODOS_PROIBIDOS = {"format", "format_map"}


class ErroDeExecucao(Exception):
    pass


def validar(arvore: ast.AST) -> None:
    for no in ast.walk(arvore):
        if not isinstance(no, NOS_PERMITIDOS):
            raise ErroDeExecucao(f"Construção não permitida: {type(no).__name__}")
        if isinstance(no, ast.Attribute) and (no.attr.startswith("_") or no.attr in METODOS_PROIBIDOS):
            raise ErroDeExecucao(f"Acesso não permitido ao atributo '{no.attr}'")
        if isinstance(no, ast.Name) and no.id.startswith("_"):
            raise ErroDeExecucao(f"Nome não permitido: '{no.id}'")


def executar(codigo: str, ferramentas: dict[str, Callable], max_linhas: int = 10_000) -> str:
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as erro:
        raise ErroDeExecucao(f"Sintaxe inválida: {erro.msg} (linha {erro.lineno})") from None
    validar(arvore)

    ambiente = {"__builtins__": {nome: getattr(builtins, nome) for nome in NOMES_SEGUROS}, **ferramentas}
    contagem = {"linhas": 0}

    def rastrear(quadro, evento, argumento):
        if evento == "line":
            contagem["linhas"] += 1
            if contagem["linhas"] > max_linhas:
                raise ErroDeExecucao("Limite de operações excedido.")
        return rastrear

    saida = io.StringIO()
    compilado = compile(arvore, "<agente>", "exec")
    sys.settrace(rastrear)
    try:
        with redirect_stdout(saida):
            exec(compilado, ambiente)
    except ErroDeExecucao:
        raise
    except Exception as erro:
        raise ErroDeExecucao(f"{type(erro).__name__}: {erro}") from None
    finally:
        sys.settrace(None)
    return saida.getvalue().strip()
