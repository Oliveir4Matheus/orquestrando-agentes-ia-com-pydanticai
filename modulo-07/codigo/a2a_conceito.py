import json
from dataclasses import dataclass, field
from enum import Enum

AGENT_CARD = {
    "name": "Agente de Pedidos da Casa Verde",
    "description": "Responde sobre status e previsão de pedidos.",
    "url": "https://agentes.casaverde.example/pedidos",
    "skills": [{"id": "status-pedido", "description": "Consulta o status de um pedido."}],
    "authentication": ["OAuth2"],
}


class Estado(Enum):
    SUBMETIDA = "submitted"
    EM_ANDAMENTO = "working"
    PRECISA_DE_ENTRADA = "input-required"
    CONCLUIDA = "completed"
    FALHOU = "failed"


TERMINAIS = {Estado.CONCLUIDA, Estado.FALHOU}


@dataclass
class Tarefa:
    id: str
    estado: Estado = Estado.SUBMETIDA
    historico: list[str] = field(default_factory=list)
    artefatos: list[str] = field(default_factory=list)

    def mudar(self, novo: Estado) -> None:
        if self.estado in TERMINAIS:
            raise ValueError("Uma tarefa em estado terminal não muda mais.")
        self.estado = novo
        self.historico.append(novo.value)


def servidor_a2a(tarefa: Tarefa, mensagem: str) -> Tarefa:
    """Agente remoto fictício: pede o código se faltar; senão, conclui com um artefato."""
    tarefa.mudar(Estado.EM_ANDAMENTO)
    if not any(c.isdigit() for c in mensagem):
        tarefa.mudar(Estado.PRECISA_DE_ENTRADA)
        return tarefa
    tarefa.artefatos.append("Pedido 1001: enviado, chega em 12/10.")
    tarefa.mudar(Estado.CONCLUIDA)
    return tarefa


print("Agent Card (descoberta):")
print(json.dumps(AGENT_CARD, ensure_ascii=False, indent=2))

tarefa = servidor_a2a(Tarefa("t-1"), "Onde está o meu pedido?")
print("\nPrimeira mensagem, sem código:", tarefa.historico)

tarefa = servidor_a2a(Tarefa("t-2"), "Pedido 1001")
print("Segunda mensagem, com código :", tarefa.historico)
print("Artefato:", tarefa.artefatos[0])
