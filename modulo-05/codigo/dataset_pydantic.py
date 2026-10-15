import json
from typing import Literal

from pydantic import BaseModel, ValidationError, field_validator


class Mensagem(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def nao_vazio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("conteúdo vazio")
        return valor


class Exemplo(BaseModel):
    messages: list[Mensagem]

    @field_validator("messages")
    @classmethod
    def termina_no_assistente(cls, valor: list[Mensagem]) -> list[Mensagem]:
        if not valor or valor[-1].role != "assistant":
            raise ValueError("a última mensagem deve ser do assistant")
        return valor


LINHAS = [
    '{"messages": [{"role": "user", "content": "Meu pedido já saiu?"}, {"role": "assistant", "content": "Foi enviado. Equipe Casa Verde"}]}',
    '{"messages": [{"role": "usuario", "content": "Oi"}, {"role": "assistant", "content": "Olá. Equipe Casa Verde"}]}',
    '{"messages": [{"role": "user", "content": "Oi"}]}',
    '{"messages": [{"role": "user", "content": "  "}, {"role": "assistant", "content": "Olá. Equipe Casa Verde"}]}',
]

for numero, linha in enumerate(LINHAS, start=1):
    try:
        exemplo = Exemplo.model_validate_json(linha)
        print(f"linha {numero}: ok ({len(exemplo.messages)} mensagens)")
    except ValidationError as erro:
        for problema in erro.errors():
            print(f"linha {numero}: {problema['loc']} -> {problema['msg']}")
