from risco import Acao, classificar

ACOES = [
    Acao("consultar_pedido", escreve=False, reversivel=True),
    Acao("reenviar_etiqueta", escreve=True, reversivel=True),
    Acao("reembolsar R$ 40", escreve=True, reversivel=False, valor=40.0),
    Acao("reembolsar R$ 250", escreve=True, reversivel=False, valor=250.0),
    Acao("alterar endereço", escreve=True, reversivel=True, valor=0.0),
    Acao("excluir conta do cliente", escreve=True, reversivel=False),
]

for acao in ACOES:
    print(f"{acao.nome:26s} -> {classificar(acao).value}")
