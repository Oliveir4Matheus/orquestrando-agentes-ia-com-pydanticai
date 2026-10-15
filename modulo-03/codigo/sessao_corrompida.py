from pydantic import ValidationError

from pydantic_ai import ModelMessagesTypeAdapter, ModelRequest, ModelResponse, TextPart, UserPromptPart

mensagens = [
    ModelRequest(parts=[UserPromptPart("Prefiro receber à tarde.")]),
    ModelResponse(parts=[TextPart("Anotado: entregas à tarde.")]),
]

dados = ModelMessagesTypeAdapter.dump_json(mensagens)
print(dados[:60])
print([m.kind for m in ModelMessagesTypeAdapter.validate_json(dados)])

try:
    ModelMessagesTypeAdapter.validate_json(b'[{"kind": "request", "parts": [{"part_kind": "inexistente"}]}]')
except ValidationError as erro:
    print("Arquivo inválido:", erro.error_count(), "erro")
    print(erro.errors()[0]["type"])
