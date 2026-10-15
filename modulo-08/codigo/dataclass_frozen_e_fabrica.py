from dataclasses import FrozenInstanceError, dataclass, field

from risco import Acao, Camada


@dataclass
class Sessao:
    cliente: str
    permissoes: set[str] = field(default_factory=set)


a = Sessao("lia")
b = Sessao("davi")
a.permissoes.add("reembolsar")
print("lia :", a.permissoes)
print("davi:", b.permissoes)

acao = Acao("reembolsar R$ 250", escreve=True, reversivel=False, valor=250.0)
try:
    acao.valor = 10.0
except FrozenInstanceError as erro:
    print("erro:", type(erro).__name__)
print("valor:", acao.valor)
print("camada:", Camada("aprovar").name)
