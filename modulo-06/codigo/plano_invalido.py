from pydantic import BaseModel, ValidationError


class Subtarefa(BaseModel):
    codigo: str
    pergunta: str


class Plano(BaseModel):
    subtarefas: list[Subtarefa]


bom = {"subtarefas": [{"codigo": "1001", "pergunta": "Qual é o status do pedido 1001?"}]}
ruim = {"subtarefas": [{"codigo": "1001"}, "pedido 1002"]}

print("Plano válido:", Plano.model_validate(bom))

try:
    Plano.model_validate(ruim)
except ValidationError as erro:
    print(f"{erro.error_count()} erros:")
    for e in erro.errors():
        print(" ", e["loc"], "->", e["msg"])
