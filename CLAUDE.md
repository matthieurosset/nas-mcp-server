# NAS MCP Server

Serveur MCP pour interagir avec Plex, Radarr, Overseerr, Bazarr, Prowlarr et Trakt.

## Installation (Claude Desktop / Claude Code)

```json
{
  "command": "uvx",
  "args": ["nas-mcp-server"],
  "env": {
    "PLEX_URL": "http://your-nas:32400",
    "PLEX_TOKEN": "your_plex_token",
    "RADARR_URL": "http://your-nas:7878",
    "RADARR_API_KEY": "your_radarr_api_key",
    "OVERSEERR_URL": "http://your-nas:5055",
    "OVERSEERR_API_KEY": "your_overseerr_api_key",
    "BAZARR_URL": "http://your-nas:6767",
    "BAZARR_API_KEY": "your_bazarr_api_key",
    "PROWLARR_URL": "http://your-nas:9696",
    "PROWLARR_API_KEY": "your_prowlarr_api_key",
    "TRAKT_CLIENT_ID": "your_trakt_client_id"
  }
}
```

## Documentation API

- **Plex API (python-plexapi)** : https://python-plexapi.readthedocs.io/en/latest/modules/library.html
- **Radarr API** : https://radarr.video/docs/api/
- **Overseerr API** : https://api-docs.overseerr.dev/
- **Bazarr API** : Swagger UI disponible dans Bazarr (System > Status)
- **Prowlarr API** : https://prowlarr.com/docs/api/
- **Trakt API** : https://trakt.docs.apiary.io/

## Attributs de notation Plex

- `rating` : Note des critiques (Rotten Tomatoes)
- `audienceRating` : Note du public (IMDB quand configuré dans Plex)

Le code utilise `audienceRating` pour afficher les notes IMDB.

## Structure du projet

```
src/nas_mcp_server/
├── __init__.py      # Export de main()
├── main.py          # Point d'entrée du serveur MCP
├── plex/
│   ├── client.py    # Client HTTP pour l'API Plex
│   └── tools.py     # Outils MCP pour Plex
├── radarr/
│   ├── client.py    # Client HTTP pour l'API Radarr
│   └── tools.py     # Outils MCP pour Radarr
├── overseerr/
│   ├── client.py    # Client HTTP pour l'API Overseerr
│   └── tools.py     # Outils MCP pour Overseerr (filmographie, demandes)
├── bazarr/
│   ├── client.py    # Client HTTP pour l'API Bazarr
│   └── tools.py     # Outils MCP pour Bazarr (sous-titres)
├── prowlarr/
│   ├── client.py    # Client HTTP pour l'API Prowlarr
│   └── tools.py     # Outils MCP pour Prowlarr (indexeurs, recherche)
├── trakt/
│   ├── client.py    # Client HTTP pour l'API Trakt
│   └── tools.py     # Outils MCP pour Trakt (découverte, tendances)
└── unified/
    └── tools.py     # Outils unifiés de haut niveau (health check, discover)
```

## Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `PLEX_URL` | URL du serveur Plex | Oui |
| `PLEX_TOKEN` | Token d'authentification Plex | Oui |
| `RADARR_URL` | URL du serveur Radarr | Non |
| `RADARR_API_KEY` | Clé API Radarr | Non |
| `OVERSEERR_URL` | URL du serveur Overseerr | Non |
| `OVERSEERR_API_KEY` | Clé API Overseerr | Non |
| `BAZARR_URL` | URL du serveur Bazarr | Non |
| `BAZARR_API_KEY` | Clé API Bazarr | Non |
| `PROWLARR_URL` | URL du serveur Prowlarr | Non |
| `PROWLARR_API_KEY` | Clé API Prowlarr | Non |
| `TRAKT_CLIENT_ID` | Client ID de l'app Trakt | Non |

## Configuration Trakt

Pour obtenir un `TRAKT_CLIENT_ID` :
1. Créer un compte sur https://trakt.tv
2. Aller sur https://trakt.tv/oauth/applications/new
3. Créer une app (nom libre, redirect URI: `urn:ietf:wg:oauth:2.0:oob`)
4. Copier le `Client ID`

## Release

Convention de versioning : `0.0.X` - incrémenter uniquement le dernier chiffre jusqu'à une version stable définitive.

Procédure pour publier une nouvelle version :

1. **Vérifier que le repo est propre** : `git status` doit afficher "nothing to commit, working tree clean"
   - S'il y a des fichiers non suivis (untracked) ou modifiés, les commiter d'abord
   - **NE JAMAIS publier si `git status` montre des changements non commités**
2. Incrémenter `version` dans `pyproject.toml`
3. Commit et push sur GitHub :
   ```bash
   git add -A && git commit -m "Bump version to X.Y.Z" && git push
   ```
4. Build et publier sur PyPI :
   ```bash
   uv build && uv publish --username __token__ --password <PYPI_TOKEN>
   ```

Le token PyPI est stocké dans `~/.pypirc`. Pour l'utiliser avec `uv publish`, extraire le password du fichier.
