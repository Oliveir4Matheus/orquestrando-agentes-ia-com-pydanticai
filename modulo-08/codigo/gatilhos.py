from dataclasses import dataclass


@dataclass
class Atendimento:
    limite_de_falhas: int = 3
    falhas_seguidas: int = 0
    escalado: bool = False

    def registrar(self, entendeu: bool) -> None:
        self.falhas_seguidas = 0 if entendeu else self.falhas_seguidas + 1
        if self.falhas_seguidas >= self.limite_de_falhas:
            self.escalado = True


atendimento = Atendimento()
for rodada, entendeu in enumerate([True, False, False, True, False, False, False], start=1):
    atendimento.registrar(entendeu)
    estado = "ESCALADO PARA UMA PESSOA" if atendimento.escalado else f"{atendimento.falhas_seguidas} falha(s) seguida(s)"
    print(f"Rodada {rodada}: {'entendeu' if entendeu else 'não entendeu'} -> {estado}")
    if atendimento.escalado:
        break
