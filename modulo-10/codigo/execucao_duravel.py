from pathlib import Path

from pydantic_ai import Agent, ModelMessagesTypeAdapter


async def executar_com_checkpoint(agente: Agent, pergunta: str, arquivo: Path, **opcoes) -> str:
    """Executa o agente gravando um ponto de retomada a cada passo. Se o arquivo existe, retoma dele."""
    historico = ModelMessagesTypeAdapter.validate_json(arquivo.read_bytes()) if arquivo.exists() else None
    prompt = None if historico else pergunta
    async with agente.iter(prompt, message_history=historico, **opcoes) as execucao:
        async for _ in execucao:
            arquivo.write_bytes(ModelMessagesTypeAdapter.dump_json(execucao.all_messages()))
    arquivo.unlink()  # concluída: o ponto de retomada não é mais necessário
    return execucao.result.output
