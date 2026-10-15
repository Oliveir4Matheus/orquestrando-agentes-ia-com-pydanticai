from pydantic_ai import Agent

from config import MODELO

BLOCOS = {
    "Instruções": (
        "Você é o atendente virtual da loja Casa Verde. Responda dúvidas de clientes "
        "sobre pedidos, entregas e trocas."
    ),
    "Contexto": (
        "Os clientes escrevem pelo chat do site, em geral pelo celular. A loja vende "
        "utensílios e decoração para a casa."
    ),
    "Requisitos": (
        "Seja cordial e direto. Não prometa nada que a loja não tenha confirmado. "
        "Nunca invente prazos, valores ou políticas."
    ),
    "Formato de saída": (
        "Escreva no máximo duas frases e termine sempre com a assinatura 'Equipe Casa Verde'."
    ),
    "Exemplos": (
        "Cliente: Meu pedido já saiu?\n"
        "Atendente: Seu pedido foi enviado e chega até 12/10. Equipe Casa Verde\n\n"
        "Cliente: Posso trocar a cor do vaso?\n"
        "Atendente: Posso verificar a troca para você; me informe o código do pedido. Equipe Casa Verde"
    ),
}


def montar_prompt(blocos: dict[str, str]) -> str:
    return "\n\n".join(f"# {titulo}\n{texto}" for titulo, texto in blocos.items())


def estimar_tokens(texto: str) -> int:
    return len(texto) // 4


INSTRUCOES = montar_prompt(BLOCOS)
agente_com_prompt = Agent(MODELO, instructions=INSTRUCOES)

if __name__ == "__main__":
    print(INSTRUCOES)
    print(f"\nTamanho aproximado: {estimar_tokens(INSTRUCOES)} tokens")
