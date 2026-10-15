from alertas import conferir
from producao import gerar_registros, painel

for titulo, registros in {
    "ontem": gerar_registros(1000, semente=1),
    "hoje": gerar_registros(1000, semente=2, taxa_de_resolucao=0.78, lentidao=1.6),
}.items():
    avisos = conferir(painel(registros))
    print(f"{titulo}:", "sem alertas" if not avisos else f"{len(avisos)} alerta(s)")
    for aviso in avisos:
        print("  ", aviso)
