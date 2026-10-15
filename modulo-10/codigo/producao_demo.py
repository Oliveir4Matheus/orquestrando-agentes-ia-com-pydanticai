from producao import gerar_registros, painel

ontem = painel(gerar_registros(1000, semente=1))
hoje = painel(gerar_registros(1000, semente=2, taxa_de_resolucao=0.78, lentidao=1.6))

print(f"{'métrica':44s} {'ontem':>8s} {'hoje':>8s}")
for nome in ontem:
    print(f"{nome:44s} {ontem[nome]:8.3f} {hoje[nome]:8.3f}")
