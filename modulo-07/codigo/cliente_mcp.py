import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

from config import MODELO
from servidor_mcp import servidor

toolset = MCPToolset(servidor)  # em produção: MCPToolset("http://localhost:8000/mcp")

agente = Agent(
    MODELO,
    toolsets=[toolset],
    instructions="Você atende clientes da Casa Verde. Use as ferramentas disponíveis e responda em uma frase.",
)
