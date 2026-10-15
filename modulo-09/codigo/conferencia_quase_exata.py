import re
import unicodedata

ARTIGOS = {"o", "a", "os", "as", "um", "uma"}


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _como_numero(texto: str) -> float | None:
    limpo = re.sub(r"[R$%\s]", "", texto)
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def _normalizar_texto(texto: str) -> str:
    palavras = re.findall(r"\w+", _sem_acento(texto).casefold())
    return " ".join(p for p in palavras if p not in ARTIGOS)


def igual_quase_exato(resposta: str, gabarito: str) -> bool:
    """Compara uma resposta curta com o gabarito, ignorando diferenças de forma."""
    numero_gabarito = _como_numero(gabarito)
    if numero_gabarito is not None:
        numero_resposta = _como_numero(resposta)
        return numero_resposta is not None and abs(numero_resposta - numero_gabarito) < 1e-9
    if "," in gabarito:
        itens_g = [_normalizar_texto(i) for i in gabarito.split(",")]
        itens_r = [_normalizar_texto(i) for i in resposta.split(",")]
        return itens_g == itens_r
    return _normalizar_texto(resposta) == _normalizar_texto(gabarito)


def nivel(passos: int, ferramentas_distintas: int) -> int:
    """Nível de dificuldade no estilo do GAIA, pelo número de passos e de ferramentas."""
    if passos <= 5 and ferramentas_distintas <= 1:
        return 1
    if passos <= 10:
        return 2
    return 3
