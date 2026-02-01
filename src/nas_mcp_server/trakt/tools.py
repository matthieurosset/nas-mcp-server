import json
from fastmcp import FastMCP
from .client import TraktClient


def register_trakt_tools(mcp: FastMCP, client: TraktClient) -> None:
    """Enregistre tous les outils Trakt sur le serveur MCP."""

    @mcp.tool()
    async def trakt_get_trending_movies(page: int = 1, limit: int = 10) -> str:
        """
        Récupère les films tendances (les plus regardés en ce moment).

        Args:
            page: Numéro de page
            limit: Nombre de résultats par page (max 100)
        """
        results = await client.get_trending_movies(page, limit)
        simplified = []
        for item in results:
            movie = item.get("movie", item)
            simplified.append({
                "title": movie.get("title"),
                "year": movie.get("year"),
                "trakt_id": movie.get("ids", {}).get("trakt"),
                "imdb_id": movie.get("ids", {}).get("imdb"),
                "tmdb_id": movie.get("ids", {}).get("tmdb"),
                "rating": movie.get("rating"),
                "votes": movie.get("votes"),
                "watchers": item.get("watchers"),
                "overview": movie.get("overview", "")[:200],
                "genres": movie.get("genres", []),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def trakt_get_popular_movies(page: int = 1, limit: int = 10) -> str:
        """
        Récupère les films les plus populaires.

        Args:
            page: Numéro de page
            limit: Nombre de résultats par page (max 100)
        """
        results = await client.get_popular_movies(page, limit)
        simplified = []
        for movie in results:
            simplified.append({
                "title": movie.get("title"),
                "year": movie.get("year"),
                "trakt_id": movie.get("ids", {}).get("trakt"),
                "imdb_id": movie.get("ids", {}).get("imdb"),
                "tmdb_id": movie.get("ids", {}).get("tmdb"),
                "rating": movie.get("rating"),
                "votes": movie.get("votes"),
                "overview": movie.get("overview", "")[:200],
                "genres": movie.get("genres", []),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def trakt_get_watched_movies(
        period: str = "weekly",
        page: int = 1,
        limit: int = 10,
    ) -> str:
        """
        Récupère les films les plus regardés (utilisateurs uniques).

        Args:
            period: Période (weekly, monthly, yearly, all)
            page: Numéro de page
            limit: Nombre de résultats par page (max 100)
        """
        results = await client.get_watched_movies(period, page, limit)
        simplified = []
        for item in results:
            movie = item.get("movie", item)
            simplified.append({
                "title": movie.get("title"),
                "year": movie.get("year"),
                "trakt_id": movie.get("ids", {}).get("trakt"),
                "imdb_id": movie.get("ids", {}).get("imdb"),
                "tmdb_id": movie.get("ids", {}).get("tmdb"),
                "rating": movie.get("rating"),
                "votes": movie.get("votes"),
                "watcher_count": item.get("watcher_count"),
                "play_count": item.get("play_count"),
                "overview": movie.get("overview", "")[:200],
                "genres": movie.get("genres", []),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def trakt_search_movie(query: str, limit: int = 10) -> str:
        """
        Recherche un film sur Trakt.

        Args:
            query: Terme de recherche
            limit: Nombre de résultats (max 100)
        """
        results = await client.search_movie(query, limit=limit)
        simplified = []
        for item in results:
            movie = item.get("movie", {})
            simplified.append({
                "title": movie.get("title"),
                "year": movie.get("year"),
                "trakt_id": movie.get("ids", {}).get("trakt"),
                "imdb_id": movie.get("ids", {}).get("imdb"),
                "tmdb_id": movie.get("ids", {}).get("tmdb"),
                "score": item.get("score"),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)
