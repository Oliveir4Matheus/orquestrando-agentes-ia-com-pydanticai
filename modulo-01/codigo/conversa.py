from agente import agente

primeira = agente.run_sync("Onde está o meu pedido 1001?")
print(primeira.output)

segunda = agente.run_sync(
    "E qual é o valor dele?", message_history=primeira.new_messages()
)
print(segunda.output)
print("Mensagens na conversa:", len(segunda.all_messages()))
