# NAS MCP Server

MCP server for managing your media server stack: **Plex**, **Radarr**, **Overseerr**, **Bazarr**, **Prowlarr**, and **Trakt.tv**.

Use natural language to browse your library, request movies, manage subtitles, search indexers, and discover trending films.

## Installation

```bash
uvx nas-mcp-server
```

## Configuration

Add to your Claude Desktop or Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "nas-mcp-server": {
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
  }
}
```

> **Note**: Only configure the services you use. Each service is optional and will be disabled if not configured.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PLEX_URL` | Plex server URL (e.g., `http://192.168.1.100:32400`) | Yes |
| `PLEX_TOKEN` | Plex authentication token ([how to find](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)) | Yes |
| `RADARR_URL` | Radarr server URL (e.g., `http://192.168.1.100:7878`) | No |
| `RADARR_API_KEY` | Radarr API key (Settings → General → API Key) | No |
| `OVERSEERR_URL` | Overseerr server URL (e.g., `http://192.168.1.100:5055`) | No |
| `OVERSEERR_API_KEY` | Overseerr API key (Settings → General → API Key) | No |
| `BAZARR_URL` | Bazarr server URL (e.g., `http://192.168.1.100:6767`) | No |
| `BAZARR_API_KEY` | Bazarr API key (Settings → General → API Key) | No |
| `PROWLARR_URL` | Prowlarr server URL (e.g., `http://192.168.1.100:9696`) | No |
| `PROWLARR_API_KEY` | Prowlarr API key (Settings → General → API Key) | No |
| `TRAKT_CLIENT_ID` | Trakt.tv Client ID ([create app](https://trakt.tv/oauth/applications)) | No |

## Features

### 🎬 Plex - Your Media Library
Browse and explore your personal media collection.
- List movies and TV shows in your library
- Get detailed information about any title
- Check watch status and progress
- View active streaming sessions
- Get personalized recommendations based on your library

### 🎥 Radarr - Movie Management
Automate movie downloads and organization.
- Search and add movies to your collection
- Monitor download progress and queue
- Manage movie quality profiles
- Remove movies from monitoring
- Check disk space and system status

### 🎭 Overseerr - Discovery & Requests
Discover new content and manage requests.
- Search for actors and view their complete filmography
- Find which movies from an actor are missing from your library
- Browse popular and trending movies
- Submit and manage movie/TV show requests
- Check request status and approval history

### 📝 Bazarr - Subtitle Management
Automate subtitle downloads for your media.
- List movies and episodes with missing subtitles
- Search and download subtitles in any language
- View subtitle download history
- Manage subtitle providers (OpenSubtitles, Addic7ed, etc.)
- Sync with Radarr/Sonarr libraries
- Reset throttled providers

### 🔍 Prowlarr - Indexer Management
Centralized indexer management for your \*arr apps.
- List and manage all configured indexers
- Test indexer connectivity
- Search across all indexers simultaneously
- View indexer statistics and performance
- Manage connected applications (Radarr, Sonarr, etc.)
- Monitor indexer health

### 📈 Trakt.tv - Trending & Discovery
Discover what's popular and trending worldwide.
- Get trending movies (most watched right now)
- Browse popular movies (highest rated + most votes)
- View most watched movies by period (weekly, monthly, yearly)
- Search the Trakt database

### 🔧 Unified Tools
High-level tools that combine multiple services.
- **System Health Check**: Get a unified status report of all your services
- **Discover Top Rated Missing**: Find highly-rated movies you don't have yet, with genre filtering

## Example Queries

Once configured, you can ask Claude things like:

- *"What movies do I have with Tom Hanks?"*
- *"Show me my recently added movies"*
- *"What's downloading right now?"*
- *"Find movies with Timothée Chalamet that I don't have"*
- *"Download French subtitles for Inception"*
- *"What are the trending movies this week?"*
- *"Show me the top 10 missing movies excluding horror and animation"*
- *"Check the health of all my services"*
- *"Search for 'Dune' on my indexers"*
- *"Which subtitle providers are working?"*

## How to Get API Keys

### Plex Token
1. Sign in to Plex Web App
2. Browse to any media item
3. Click "Get Info" → "View XML"
4. Find `X-Plex-Token` in the URL

### Radarr / Sonarr / Prowlarr / Bazarr API Key
1. Open the application web UI
2. Go to Settings → General
3. Copy the API Key

### Overseerr API Key
1. Open Overseerr web UI
2. Go to Settings → General
3. Copy the API Key

### Trakt Client ID
1. Go to [Trakt API Applications](https://trakt.tv/oauth/applications)
2. Create a new application
3. Copy the Client ID

## License

MIT
