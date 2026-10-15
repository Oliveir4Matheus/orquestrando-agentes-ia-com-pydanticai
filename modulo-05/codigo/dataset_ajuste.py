import json
import re

ASSINATURA = "Equipe Casa Verde"
MINIMO_RECOMENDADO = 1000

CONVERSAS = [
    ("Meu pedido já saiu?", f"Seu pedido foi enviado e chega até 12/10. {ASSINATURA}"),
    ("Posso trocar a cor do vaso?", f"Posso verificar a troca; me informe o código do pedido. {ASSINATURA}"),
    ("Onde está meu pedido?", f"Pode me passar o código do pedido para eu consultar? {ASSINATURA}"),
    ("Meu pedido já saiu?", f"Seu pedido foi enviado e chega até 12/10. {ASSINATURA}"),
    ("Liguem para 11 98765-4321", f"Retornaremos para o número informado. {ASSINATURA}"),
    ("Quero cancelar o pedido.", "Claro, vou cancelar para você."),
    ("", f"Como posso ajudar? {ASSINATURA}"),
]


def validar(pergunta: str, resposta: str) -> str | None:
    if not pergunta.strip():
        return "pergunta vazia"
    if not resposta.rstrip().endswith(ASSINATURA):
        return "sem a assinatura padrão"
    if re.search(r"\d{2}\s?9?\d{4}-\d{4}", pergunta + resposta):
        return "contém telefone (dado pessoal)"
    return None


def montar(conversas) -> tuple[list[dict], dict[str, int]]:
    exemplos, descartes, vistos = [], {}, set()
    for pergunta, resposta in conversas:
        motivo = validar(pergunta, resposta)
        if motivo is None and (pergunta, resposta) in vistos:
            motivo = "duplicada"
        if motivo:
            descartes[motivo] = descartes.get(motivo, 0) + 1
            continue
        vistos.add((pergunta, resposta))
        exemplos.append({"messages": [
            {"role": "system", "content": "Você é o atendente virtual da loja Casa Verde."},
            {"role": "user", "content": pergunta},
            {"role": "assistant", "content": resposta},
        ]})
    return exemplos, descartes


exemplos, descartes = montar(CONVERSAS)
print(f"Conversas recebidas: {len(CONVERSAS)}")
print(f"Exemplos válidos   : {len(exemplos)}")
for motivo, quantidade in descartes.items():
    print(f"  descartado ({motivo}): {quantidade}")
if len(exemplos) < MINIMO_RECOMENDADO:
    print(f"Atenção: o ajuste costuma pedir pelo menos alguns milhares de exemplos; você tem {len(exemplos)}.")
print("\nPrimeira linha do arquivo JSONL:")
print(json.dumps(exemplos[0], ensure_ascii=False))
