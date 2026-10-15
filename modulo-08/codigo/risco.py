from dataclasses import dataclass
from enum import Enum


class Camada(Enum):
    AUTONOMA = "autônoma"
    NOTIFICAR = "notificar"
    APROVAR = "aprovar"


@dataclass(frozen=True)
class Acao:
    nome: str
    escreve: bool  # altera dados ou o mundo?
    reversivel: bool  # dá para desfazer?
    valor: float = 0.0  # impacto financeiro, em reais


LIMITE_DE_VALOR = 100.0


def classificar(acao: Acao) -> Camada:
    """Classificação determinística: nenhuma parte dela passa por um modelo."""
    if not acao.escreve:
        return Camada.AUTONOMA
    if acao.valor > LIMITE_DE_VALOR:
        return Camada.APROVAR
    if not acao.reversivel and acao.valor == 0:  # destrutiva e sem valor para medir: alto risco
        return Camada.APROVAR
    return Camada.NOTIFICAR
