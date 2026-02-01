import os
from typing import Any

import httpx


class TraktClient:
    """Client HTTP pour l'API Trakt.tv."""

    def __init__(self):
        self.client_id = os.getenv("TRAKT_CLIENT_ID")
        if not self.client_id:
            raise ValueError("TRAKT_CLIENT_ID is required")

        self.base_url = "https://api.trakt.tv"
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Effectue une requête HTTP vers l'API Trakt."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_trending_movies(
        self,
        page: int = 1,
        limit: int = 10,
        extended: str = "full",
    ) -> list[dict[str, Any]]:
        """
        Récupère les films tendances (les plus regardés en ce moment).

        Args:
            page: Numéro de page
            limit: Nombre de résultats par page
            extended: Niveau de détail (full pour plus d'infos)
        """
        params = {"page": page, "limit": limit, "extended": extended}
        return await self._request("GET", "/movies/trending", params=params)

    async def get_popular_movies(
        self,
        page: int = 1,
        limit: int = 10,
        extended: str = "full",
    ) -> list[dict[str, Any]]:
        """
        Récupère les films les plus populaires.
        Popularité = combinaison note + nombre de votes.

        Args:
            page: Numéro de page
            limit: Nombre de résultats par page
            extended: Niveau de détail
        """
        params = {"page": page, "limit": limit, "extended": extended}
        return await self._request("GET", "/movies/popular", params=params)

    async def get_watched_movies(
        self,
        period: str = "weekly",
        page: int = 1,
        limit: int = 10,
        extended: str = "full",
    ) -> list[dict[str, Any]]:
        """
        Récupère les films les plus regardés (utilisateurs uniques).

        Args:
            period: Période (weekly, monthly, yearly, all)
            page: Numéro de page
            limit: Nombre de résultats par page
            extended: Niveau de détail
        """
        params = {"page": page, "limit": limit, "extended": extended}
        return await self._request("GET", f"/movies/watched/{period}", params=params)

    async def get_played_movies(
        self,
        period: str = "weekly",
        page: int = 1,
        limit: int = 10,
        extended: str = "full",
    ) -> list[dict[str, Any]]:
        """
        Récupère les films les plus joués (un utilisateur peut regarder plusieurs fois).

        Args:
            period: Période (weekly, monthly, yearly, all)
            page: Numéro de page
            limit: Nombre de résultats par page
            extended: Niveau de détail
        """
        params = {"page": page, "limit": limit, "extended": extended}
        return await self._request("GET", f"/movies/played/{period}", params=params)

    async def get_movie(
        self,
        trakt_id: str,
        extended: str = "full",
    ) -> dict[str, Any]:
        """
        Récupère les détails d'un film.

        Args:
            trakt_id: ID Trakt, IMDB (tt...) ou slug
            extended: Niveau de détail
        """
        params = {"extended": extended}
        return await self._request("GET", f"/movies/{trakt_id}", params=params)

    async def search_movie(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Recherche un film par titre.

        Args:
            query: Terme de recherche
            page: Numéro de page
            limit: Nombre de résultats
        """
        params = {"query": query, "type": "movie", "page": page, "limit": limit}
        return await self._request("GET", "/search/movie", params=params)
