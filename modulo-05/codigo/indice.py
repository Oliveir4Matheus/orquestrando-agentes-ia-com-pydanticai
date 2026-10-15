import math
import re
import unicodedata
import zlib
from dataclasses import dataclass

DIMENSOES = 1024
PALAVRAS_VAZIAS = {
    "de", "da", "do", "das", "dos", "a", "o", "as", "os", "e", "em", "no", "na", "para",
    "que", "um", "uma", "com", "por", "se", "ao", "ou", "pelo", "pela", "é", "são",
}


def palavras(texto: str) -> list[str]:
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return [p for p in re.findall(r"\w+", sem_acento) if p not in PALAVRAS_VAZIAS]


def embedar_lexico(textos: list[str]) -> list[list[float]]:
    """Vetor de contagem de palavras (com hash), normalizado. Offline e determinístico."""
    vetores = []
    for texto in textos:
        vetor = [0.0] * DIMENSOES
        for palavra in palavras(texto):
            vetor[zlib.crc32(palavra.encode()) % DIMENSOES] += 1.0
        norma = math.sqrt(sum(x * x for x in vetor)) or 1.0
        vetores.append([x / norma for x in vetor])
    return vetores


@dataclass
class Fragmento:
    id: str
    titulo: str
    texto: str


class Indice:
    def __init__(self, fragmentos: list[Fragmento], embedar=embedar_lexico):
        self.fragmentos = fragmentos
        self.embedar = embedar
        self.vetores = embedar([f"{f.titulo}. {f.texto}" for f in fragmentos])

    def buscar(self, pergunta: str, k: int = 2) -> list[tuple[float, Fragmento]]:
        consulta = self.embedar([pergunta])[0]
        pontos = [
            (sum(a * b for a, b in zip(consulta, vetor)), fragmento)
            for vetor, fragmento in zip(self.vetores, self.fragmentos)
        ]
        return sorted(pontos, key=lambda par: par[0], reverse=True)[:k]


def dividir(texto: str, tamanho: int, sobreposicao: int) -> list[str]:
    """Divide um texto em trechos de `tamanho` caracteres, repetindo `sobreposicao` no começo do seguinte."""
    passo = tamanho - sobreposicao
    return [texto[inicio : inicio + tamanho] for inicio in range(0, len(texto), passo)]
