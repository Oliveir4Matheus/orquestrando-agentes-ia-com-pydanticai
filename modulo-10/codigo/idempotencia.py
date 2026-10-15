import json
from pathlib import Path


class Livro:
    """Registro de efeitos: a mesma chamada, com a mesma chave, só produz efeito uma vez."""

    def __init__(self, arquivo: Path):
        self.arquivo = arquivo
        self.dados = json.loads(arquivo.read_text()) if arquivo.exists() else {}

    def executar_uma_vez(self, chave: str, efeito):
        if chave in self.dados:
            return self.dados[chave]
        resultado = efeito()
        self.dados[chave] = resultado
        self.arquivo.write_text(json.dumps(self.dados))
        return resultado
