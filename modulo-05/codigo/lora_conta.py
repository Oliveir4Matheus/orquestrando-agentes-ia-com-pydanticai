D_MODELO = 12_288  # dimensão das matrizes de atenção do GPT-3 175B
CAMADAS = 96  # número de camadas do GPT-3 175B
PARAMETROS_TOTAIS = 175_000_000_000


def parametros_completos(d: int, k: int) -> int:
    return d * k


def parametros_lora(d: int, k: int, r: int) -> int:
    return r * (d + k)


print("Uma matriz de atenção de 12.288 x 12.288:")
completo = parametros_completos(D_MODELO, D_MODELO)
print(f"  ajuste completo: {completo:,} parâmetros")
for r in (1, 2, 4, 8):
    lora = parametros_lora(D_MODELO, D_MODELO, r)
    print(f"  LoRA com r={r}: {lora:>9,} parâmetros ({completo / lora:,.0f}x menos)")

r = 4
matrizes_por_camada = 2  # as projeções de consulta (Wq) e valor (Wv)
total_lora = CAMADAS * matrizes_por_camada * parametros_lora(D_MODELO, D_MODELO, r)
print(f"\nModelo inteiro, r={r}, Wq e Wv em {CAMADAS} camadas:")
print(f"  parâmetros treináveis: {total_lora:,}")
print(f"  redução sobre o ajuste completo: {PARAMETROS_TOTAIS / total_lora:,.0f}x")
