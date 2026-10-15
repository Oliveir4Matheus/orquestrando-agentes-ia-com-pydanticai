import asyncio
import uuid
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_ai.usage import UsageLimits

from config import MODELO

agente = Agent(
    MODELO,
    name="atendente",
    instructions="Você atende clientes da Casa Verde em até duas frases.",
)


def criar_app(pasta_de_sessoes: Path, chave_de_api: str, tempo_maximo: float = 20.0, simultaneas: int = 8) -> Starlette:
    pasta_de_sessoes.mkdir(parents=True, exist_ok=True)
    vagas = asyncio.Semaphore(simultaneas)

    def caminho(conversa: str) -> Path:
        return pasta_de_sessoes / f"{conversa}.json"

    async def saude(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def enviar_mensagem(request: Request) -> JSONResponse:
        id_da_requisicao = str(uuid.uuid4())[:8]
        if request.headers.get("x-api-key") != chave_de_api:
            return JSONResponse({"erro": "não autorizado"}, status_code=401)

        try:
            texto = (await request.json())["texto"]
            conversa = request.path_params["conversa"]
            if not isinstance(texto, str) or not texto.strip() or not conversa.isalnum():
                raise ValueError
        except (ValueError, KeyError, TypeError):
            return JSONResponse({"erro": "corpo inválido"}, status_code=400)

        if vagas.locked():
            return JSONResponse({"erro": "sistema ocupado, tente de novo"}, status_code=429)

        async with vagas:
            arquivo = caminho(conversa)
            historico = ModelMessagesTypeAdapter.validate_json(arquivo.read_bytes()) if arquivo.exists() else None
            try:
                resultado = await asyncio.wait_for(
                    agente.run(texto, message_history=historico, usage_limits=UsageLimits(request_limit=10)),
                    timeout=tempo_maximo,
                )
            except asyncio.TimeoutError:
                return JSONResponse({"erro": "tempo esgotado", "id": id_da_requisicao}, status_code=504)
            arquivo.write_bytes(ModelMessagesTypeAdapter.dump_json(resultado.all_messages()))

        return JSONResponse({
            "resposta": resultado.output,
            "mensagens_na_conversa": len(resultado.all_messages()),
            "chamadas_ao_modelo": resultado.usage.requests,
            "id": id_da_requisicao,
        })

    return Starlette(routes=[
        Route("/saude", saude),
        Route("/conversas/{conversa}/mensagens", enviar_mensagem, methods=["POST"]),
    ])
