from executor import ErroDeExecucao, executar

TENTATIVAS = {
    "código legítimo": "total = 0\nfor n in range(4):\n    total += n\nprint(total)",
    "importar módulo": "import os\nprint(os.listdir('.'))",
    "acessar atributo interno": "print(().__class__)",
    "abrir arquivo": "print(open('segredo.txt').read())",
    "truque com format": "print('{0.__class__}'.format(1))",
    "definir função": "def f():\n    return 1\nprint(f())",
    "laço infinito": "while True:\n    pass",
}

for nome, codigo in TENTATIVAS.items():
    try:
        print(f"{nome:26s} -> executado: {executar(codigo, {})}")
    except ErroDeExecucao as erro:
        print(f"{nome:26s} -> bloqueado: {erro}")
