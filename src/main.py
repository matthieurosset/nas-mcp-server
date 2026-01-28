import os
import sys
import logging
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Prompt, PromptMessage, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("nas-mcp-server")

# Créer le serveur MCP
mcp = Server("nas-mcp-server")

# Prompt guide pour l'IA
GUIDE = """
# NAS Media Server Guide

## Services disponibles

### Plex - Ta médiathèque
Utilise Plex quand l'utilisateur parle de :
- "ma bibliothèque", "mes films", "mes séries"
- "ce que j'ai", "déjà vu", "pas encore vu"
- "recommandations", "suggestions"

### Radarr - Gestionnaire de films
Utilise Radarr quand l'utilisateur veut :
- ajouter/télécharger un nouveau film
- voir les téléchargements en cours
- supprimer un film de la surveillance
"""

@mcp.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="nas-guide",
            description="Guide d'utilisation des services NAS média",
        )
    ]

@mcp.get_prompt()
async def get_prompt(name: str) -> list[PromptMessage]:
    if name == "nas-guide":
        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=GUIDE)
            )
        ]
    raise ValueError(f"Prompt inconnu: {name}")

# Importer et enregistrer les outils Radarr
from radarr import RadarrClient, register_radarr_tools

try:
    radarr_client = RadarrClient()
    register_radarr_tools(mcp, radarr_client)
    logger.info("Radarr tools registered successfully")
except ValueError as e:
    logger.warning(f"Radarr not configured: {e}")

# Importer et enregistrer les outils Plex
from plex import PlexClient, register_plex_tools

try:
    plex_client = PlexClient()
    register_plex_tools(mcp, plex_client)
    logger.info("Plex tools registered successfully")
except ValueError as e:
    logger.warning(f"Plex not configured: {e}")


# Transport SSE
sse = SseServerTransport("/messages/")


async def handle_sse(request):
    """Gère les connexions SSE entrantes."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.run(
            streams[0], streams[1], mcp.create_initialization_options()
        )


async def handle_messages(request):
    """Gère les messages POST du client."""
    await sse.handle_post_message(request.scope, request.receive, request._send)


async def health_check(request):
    """Endpoint de santé pour Docker/Kubernetes."""
    return JSONResponse({"status": "healthy", "server": "nas-mcp-server"})


# Application Starlette
app = Starlette(
    debug=False,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages/", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=health_check),
    ],
)


def main():
    """Point d'entrée principal."""
    port = int(os.getenv("MCP_PORT", "3001"))
    host = os.getenv("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting NAS MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
