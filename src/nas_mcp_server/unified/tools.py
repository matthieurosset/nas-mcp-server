import asyncio
import json
from fastmcp import FastMCP

from ..plex.client import PlexClient
from ..radarr.client import RadarrClient
from ..overseerr.client import OverseerrClient
from ..bazarr.client import BazarrClient
from ..prowlarr.client import ProwlarrClient
from ..trakt.client import TraktClient


def register_unified_tools(
    mcp: FastMCP,
    plex_client: PlexClient | None = None,
    radarr_client: RadarrClient | None = None,
    overseerr_client: OverseerrClient | None = None,
    bazarr_client: BazarrClient | None = None,
    prowlarr_client: ProwlarrClient | None = None,
    trakt_client: TraktClient | None = None,
) -> None:
    """Enregistre les outils unifiés de haut niveau."""

    @mcp.tool()
    async def system_health_check() -> str:
        """
        Vérifie l'état de santé de tous les services du NAS.

        Retourne un rapport unifié avec le statut de chaque service
        (Plex, Radarr, Overseerr, Bazarr, Prowlarr).
        """

        async def check_plex() -> dict:
            if plex_client is None:
                return {"status": "not_configured"}
            try:
                server_info = await plex_client.get_server_info()
                sessions = await plex_client.get_active_sessions()
                return {
                    "status": "online",
                    "version": server_info.get("version"),
                    "name": server_info.get("friendlyName"),
                    "platform": server_info.get("platform"),
                    "active_sessions": len(sessions),
                }
            except Exception as e:
                return {"status": "offline", "error": str(e)}

        async def check_radarr() -> dict:
            if radarr_client is None:
                return {"status": "not_configured"}
            try:
                status = await radarr_client.get_system_status()
                movies = await radarr_client.get_movies()
                queue = await radarr_client.get_queue()
                monitored = sum(1 for m in movies if m.get("monitored", False))
                return {
                    "status": "online",
                    "version": status.get("version"),
                    "movies_total": len(movies),
                    "movies_monitored": monitored,
                    "queue_count": queue.get("totalRecords", 0),
                }
            except Exception as e:
                return {"status": "offline", "error": str(e)}

        async def check_overseerr() -> dict:
            if overseerr_client is None:
                return {"status": "not_configured"}
            try:
                status = await overseerr_client.get_status()
                requests = await overseerr_client.get_requests(take=100)
                pending = sum(1 for r in requests.get("results", [])
                             if r.get("status") == 1)  # 1 = pending
                return {
                    "status": "online",
                    "version": status.get("version"),
                    "pending_requests": pending,
                }
            except Exception as e:
                return {"status": "offline", "error": str(e)}

        async def check_bazarr() -> dict:
            if bazarr_client is None:
                return {"status": "not_configured"}
            try:
                status = await bazarr_client.get_system_status()
                providers = await bazarr_client.get_providers()
                movies_wanted = await bazarr_client.get_movies_wanted(length=1000)
                episodes_wanted = await bazarr_client.get_episodes_wanted(length=1000)

                providers_list = providers.get("data", [])
                providers_ok = sum(1 for p in providers_list if p.get("status") == "Good")
                providers_throttled = sum(1 for p in providers_list if p.get("status") != "Good")

                return {
                    "status": "online",
                    "version": status.get("version"),
                    "providers_ok": providers_ok,
                    "providers_throttled": providers_throttled,
                    "missing_movie_subtitles": len(movies_wanted.get("data", [])),
                    "missing_episode_subtitles": len(episodes_wanted.get("data", [])),
                }
            except Exception as e:
                return {"status": "offline", "error": str(e)}

        async def check_prowlarr() -> dict:
            if prowlarr_client is None:
                return {"status": "not_configured"}
            try:
                status = await prowlarr_client.get_system_status()
                health = await prowlarr_client.get_health()
                indexers = await prowlarr_client.get_indexers()

                indexers_enabled = sum(1 for i in indexers if i.get("enable", False))
                indexers_disabled = len(indexers) - indexers_enabled
                health_issues = [h.get("message") for h in health] if health else []

                return {
                    "status": "online",
                    "version": status.get("version"),
                    "indexers_total": len(indexers),
                    "indexers_enabled": indexers_enabled,
                    "indexers_disabled": indexers_disabled,
                    "health_issues": health_issues,
                }
            except Exception as e:
                return {"status": "offline", "error": str(e)}

        # Exécuter tous les checks en parallèle
        results = await asyncio.gather(
            check_plex(),
            check_radarr(),
            check_overseerr(),
            check_bazarr(),
            check_prowlarr(),
        )

        services = {
            "plex": results[0],
            "radarr": results[1],
            "overseerr": results[2],
            "bazarr": results[3],
            "prowlarr": results[4],
        }

        # Calculer le statut global
        configured_services = [s for s in services.values() if s["status"] != "not_configured"]
        online_services = [s for s in configured_services if s["status"] == "online"]
        offline_services = [s for s in configured_services if s["status"] == "offline"]

        # Vérifier les warnings (providers throttled, health issues)
        has_warnings = False
        warnings = []

        if services["bazarr"].get("providers_throttled", 0) > 0:
            has_warnings = True
            warnings.append(f"Bazarr: {services['bazarr']['providers_throttled']} provider(s) throttled")

        if services["prowlarr"].get("health_issues"):
            has_warnings = True
            warnings.append(f"Prowlarr: {len(services['prowlarr']['health_issues'])} problème(s)")

        # Déterminer overall_status
        if offline_services:
            overall_status = "critical"
        elif has_warnings:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        # Construire le résumé
        summary_parts = []
        summary_parts.append(f"{len(online_services)}/{len(configured_services)} services online")
        if offline_services:
            offline_names = [name for name, s in services.items() if s["status"] == "offline"]
            summary_parts.append(f"Offline: {', '.join(offline_names)}")
        if warnings:
            summary_parts.extend(warnings)

        response = {
            "overall_status": overall_status,
            "services": services,
            "summary": ". ".join(summary_parts) + ".",
        }

        return json.dumps(response, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def discover_top_rated_missing(
        source: str = "popular",
        period: str = "weekly",
        min_imdb_rating: float = 6.0,
        limit: int = 10,
        exclude_genres: list[str] | None = None,
    ) -> str:
        """
        Découvre les films bien notés que tu n'as pas encore dans ta collection.

        Args:
            source: Source Trakt (popular, trending, watched)
            period: Période pour 'watched' (weekly, monthly, yearly, all)
            min_imdb_rating: Note IMDB minimum (défaut: 6.0)
            limit: Nombre de films à retourner (défaut: 10)
            exclude_genres: Liste de genres à exclure (ex: ["animation", "anime"])
        """
        if trakt_client is None:
            return json.dumps({
                "error": "Trakt not configured",
                "message": "TRAKT_CLIENT_ID is required"
            }, indent=2)

        if radarr_client is None:
            return json.dumps({
                "error": "Radarr not configured",
                "message": "Radarr is required to check your collection and get IMDB ratings"
            }, indent=2)

        # 1. Récupérer les films depuis Trakt (on en prend plus pour filtrer ensuite)
        fetch_limit = max(100, limit * 10)  # Minimum 100, sinon 10x le limit
        try:
            if source == "trending":
                trakt_movies = await trakt_client.get_trending_movies(limit=fetch_limit)
            elif source == "watched":
                trakt_movies = await trakt_client.get_watched_movies(period=period, limit=fetch_limit)
            else:  # popular par défaut
                trakt_movies = await trakt_client.get_popular_movies(limit=fetch_limit)
        except Exception as e:
            return json.dumps({
                "error": "Trakt API error",
                "message": str(e)
            }, indent=2)

        # 2. Récupérer la collection Radarr
        try:
            radarr_movies = await radarr_client.get_movies()
            # Créer un set des TMDB IDs qu'on a déjà
            owned_tmdb_ids = {m.get("tmdbId") for m in radarr_movies if m.get("tmdbId")}
        except Exception as e:
            return json.dumps({
                "error": "Radarr API error",
                "message": str(e)
            }, indent=2)

        # 3. Extraire les films Trakt, filtrer ceux qu'on a déjà et pré-filtrer par note Trakt
        candidates = []
        for item in trakt_movies:
            # Trakt retourne soit {movie: {...}} soit directement {...}
            movie = item.get("movie", item)
            ids = movie.get("ids", {})
            tmdb_id = ids.get("tmdb")
            trakt_rating = movie.get("rating")

            # Skip si on l'a déjà
            if tmdb_id in owned_tmdb_ids:
                continue

            # Pré-filtrer par note Trakt (approximation de la note IMDB)
            # On garde une marge de -0.5 car Trakt et IMDB peuvent différer
            if trakt_rating and trakt_rating < (min_imdb_rating - 0.5):
                continue

            # Filtrer par genres exclus
            movie_genres = [g.lower() for g in movie.get("genres", [])]
            if exclude_genres:
                excluded = [g.lower() for g in exclude_genres]
                if any(g in movie_genres for g in excluded):
                    continue

            candidates.append({
                "title": movie.get("title"),
                "year": movie.get("year"),
                "imdb_id": ids.get("imdb"),
                "tmdb_id": tmdb_id,
                "trakt_id": ids.get("trakt"),
                "trakt_rating": trakt_rating,
                "overview": movie.get("overview", "")[:300],
                "genres": movie.get("genres", []),
            })

        # 4. Trier par note Trakt décroissante et limiter avant enrichissement IMDB
        candidates.sort(key=lambda x: x.get("trakt_rating") or 0, reverse=True)
        # On enrichit seulement limit * 2 films (marge pour le filtrage IMDB final)
        candidates_to_enrich = candidates[:limit * 2]

        # 5. Enrichir avec les notes IMDB via Radarr (en parallèle)
        async def fetch_imdb_rating(movie: dict) -> dict:
            tmdb_id = movie.get("tmdb_id")
            if not tmdb_id:
                movie["imdb_rating"] = None
                return movie
            try:
                results = await radarr_client.search_movie(f"tmdb:{tmdb_id}")
                if results:
                    imdb_rating = results[0].get("ratings", {}).get("imdb", {}).get("value")
                    movie["imdb_rating"] = imdb_rating
                else:
                    movie["imdb_rating"] = None
            except Exception:
                movie["imdb_rating"] = None
            return movie

        enriched = await asyncio.gather(*[fetch_imdb_rating(m) for m in candidates_to_enrich])

        # 6. Filtrer par note IMDB minimum
        filtered = [m for m in enriched if m.get("imdb_rating") and m["imdb_rating"] >= min_imdb_rating]

        # 7. Trier par note IMDB décroissante
        filtered.sort(key=lambda x: x.get("imdb_rating", 0), reverse=True)

        # 8. Retourner les top `limit`
        result = filtered[:limit]

        return json.dumps({
            "source": source,
            "period": period if source == "watched" else None,
            "min_imdb_rating": min_imdb_rating,
            "exclude_genres": exclude_genres,
            "count": len(result),
            "movies": result,
        }, indent=2, ensure_ascii=False)
