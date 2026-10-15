import random
import statistics
from dataclasses import dataclass


@dataclass
class Registro:
    """O que se guarda de cada atendimento em produção (sem o conteúdo da conversa)."""

    id: str
    resolveu: bool | None  # None: ainda sem rótulo
    latencia_s: float
    tokens: int
    guardrail_acionado: bool
    dado_pessoal_na_saida: bool
    escalou_para_humano: bool


CUSTO_POR_MIL_TOKENS = 0.02  # valor hipotético, em reais


def gerar_registros(n: int, semente: int, taxa_de_resolucao: float = 0.85, lentidao: float = 1.0) -> list[Registro]:
    sorteio = random.Random(semente)
    registros = []
    for i in range(n):
        registros.append(Registro(
            id=f"a{semente}-{i}",
            resolveu=sorteio.random() < taxa_de_resolucao,
            latencia_s=max(0.3, sorteio.gauss(2.0 * lentidao, 0.5)),
            tokens=int(sorteio.gauss(1800, 300)),
            guardrail_acionado=sorteio.random() < 0.03,
            dado_pessoal_na_saida=sorteio.random() < 0.002,
            escalou_para_humano=sorteio.random() < 0.08,
        ))
    return registros


def percentil(valores: list[float], p: float) -> float:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(p * len(ordenados)))]


def painel(registros: list[Registro]) -> dict[str, float]:
    n = len(registros)
    rotulados = [r for r in registros if r.resolveu is not None]
    return {
        "qualidade: taxa de resolução": sum(r.resolveu for r in rotulados) / len(rotulados),
        "desempenho: latência p50 (s)": percentil([r.latencia_s for r in registros], 0.50),
        "desempenho: latência p95 (s)": percentil([r.latencia_s for r in registros], 0.95),
        "responsabilidade: guardrails acionados": sum(r.guardrail_acionado for r in registros) / n,
        "responsabilidade: dado pessoal na saída": sum(r.dado_pessoal_na_saida for r in registros) / n,
        "custo: R$ por atendimento": statistics.mean(r.tokens for r in registros) / 1000 * CUSTO_POR_MIL_TOKENS,
        "supervisão: escalonamentos para humano": sum(r.escalou_para_humano for r in registros) / n,
    }
