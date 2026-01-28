import os
import sys
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

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
mcp = FastMCP("nas-mcp-server")

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

@mcp.prompt()
def nas_guide() -> str:
    """Guide d'utilisation des services NAS média."""
    return GUIDE

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


def main():
    """Point d'entrée principal."""
    port = int(os.getenv("MCP_PORT", "3001"))
    host = os.getenv("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting NAS MCP Server on {host}:{port}")
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    main()
