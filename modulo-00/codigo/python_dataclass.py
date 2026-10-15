from dataclasses import dataclass, field


@dataclass
class Loja:
    nome: str
    frete_gratis_acima: float = 200.0
    pedidos: dict[str, str] = field(default_factory=dict)


casa_verde = Loja("Casa Verde", pedidos={"1001": "enviado"})
print(casa_verde)
print(casa_verde.pedidos["1001"])
print(casa_verde == Loja("Casa Verde", 200.0, {"1001": "enviado"}))
print(Loja("Casa Verde", frete_gratis_acima="barato").frete_gratis_acima)
