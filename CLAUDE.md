# NAS MCP Server

Serveur MCP pour interagir avec Plex et Radarr.

## Documentation API

- **Plex API (python-plexapi)** : https://python-plexapi.readthedocs.io/en/latest/modules/library.html
- **Radarr API** : https://radarr.video/docs/api/

## Attributs de notation Plex

- `rating` : Note des critiques (Rotten Tomatoes)
- `audienceRating` : Note du public (IMDB quand configuré dans Plex)

Le code utilise `audienceRating` pour afficher les notes IMDB.

## Déploiement des changements

Après modification du code, redémarrer le serveur MCP pour appliquer les changements :

```bash
# Si lancé via Claude Desktop, redémarrer Claude Desktop
# Si lancé manuellement :
uv run python -m src.main
```

## Structure du projet

```
src/
├── main.py          # Point d'entrée du serveur MCP
├── plex/
│   ├── client.py    # Client HTTP pour l'API Plex
│   └── tools.py     # Outils MCP pour Plex
└── radarr/
    ├── client.py    # Client HTTP pour l'API Radarr
    └── tools.py     # Outils MCP pour Radarr
```

## Variables d'environnement

```
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your_radarr_api_key
```
