import pydantic
import pydantic_ai
import pydantic_evals
import pydantic_graph
import logfire

for pacote in (pydantic, pydantic_ai, pydantic_evals, pydantic_graph, logfire):
    print(pacote.__name__, "importado")

print("pydantic", pydantic.VERSION)
print("pydantic_ai", pydantic_ai.__version__)
