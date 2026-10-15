import re

LIMITE_DE_CARACTERES = 600

PADROES_PROIBIDOS = [
    r"ignore\s+(todas\s+)?as\s+instru[cç][õo]es",
    r"revele\s+(o\s+)?(seu\s+)?prompt",
    r";\s*drop\s+table",
    r"<script",
]

PADROES_DE_DADOS_PESSOAIS = {
    "cpf": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
    "telefone": r"\b\(?\d{2}\)?\s?9?\d{4}-\d{4}\b",
    "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
}


def violacao_de_regra(mensagem: str) -> str | None:
    """Camada determinística: devolve o motivo do bloqueio, ou None se a mensagem passa."""
    if len(mensagem) > LIMITE_DE_CARACTERES:
        return f"mensagem acima de {LIMITE_DE_CARACTERES} caracteres"
    for padrao in PADROES_PROIBIDOS:
        if re.search(padrao, mensagem, flags=re.IGNORECASE):
            return "padrão proibido na mensagem"
    return None


def mascarar_dados_pessoais(texto: str) -> str:
    for nome, padrao in PADROES_DE_DADOS_PESSOAIS.items():
        texto = re.sub(padrao, f"[{nome} removido]", texto)
    return texto
