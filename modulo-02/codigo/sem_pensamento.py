from consulta import agente
from trajetoria import mostrar

resultado = agente.run_sync("Meu pedido 1003 chegou com defeito. Ainda consigo devolver?")
mostrar(resultado)
