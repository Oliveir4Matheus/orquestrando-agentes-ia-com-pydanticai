import tempfile
from pathlib import Path

from starlette.testclient import TestClient

import modelos_simulados as sim
import servico

CHAVE = "segredo-de-teste"
app = servico.criar_app(Path(tempfile.mkdtemp()), CHAVE, tempo_maximo=0.2)
cliente = TestClient(app)
cabecalho = {"x-api-key": CHAVE}

print("GET /saude ->", cliente.get("/saude").json())

with servico.agente.override(model=sim.texto("Seu pedido 1001 foi enviado.")):
    r = cliente.post("/conversas/lia1/mensagens", json={"texto": "Onde está o pedido 1001?"}, headers=cabecalho)
    print("1ª mensagem ->", r.status_code, {k: r.json()[k] for k in ("resposta", "mensagens_na_conversa")})

    r = cliente.post("/conversas/lia1/mensagens", json={"texto": "E a previsão?"}, headers=cabecalho)
    print("2ª mensagem ->", r.status_code, {k: r.json()[k] for k in ("resposta", "mensagens_na_conversa")})

    r = cliente.post("/conversas/lia1/mensagens", json={"texto": "oi"})
    print("sem chave   ->", r.status_code, r.json())

    r = cliente.post("/conversas/lia1/mensagens", json={"texto": "   "}, headers=cabecalho)
    print("corpo vazio ->", r.status_code, r.json())

with servico.agente.override(model=sim.texto("devagar", espera=1.0)):
    r = cliente.post("/conversas/lia2/mensagens", json={"texto": "Olá"}, headers=cabecalho)
    print("modelo lento ->", r.status_code, r.json()["erro"])
