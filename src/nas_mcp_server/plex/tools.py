import json
from fastmcp import FastMCP
from .client import PlexClient


def register_plex_tools(mcp: FastMCP, client: PlexClient) -> None:
    """Enregistre tous les outils Plex sur le serveur MCP."""

    @mcp.tool()
    async def plex_get_libraries() -> str:
        """Liste toutes les bibliothèques Plex (Films, Séries, Musique, etc.)."""
        libraries = await client.get_libraries()
        simplified = []
        for lib in libraries:
            simplified.append({
                "key": lib.get("key"),
                "title": lib.get("title"),
                "type": lib.get("type"),
                "agent": lib.get("agent"),
                "scanner": lib.get("scanner"),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_search(
        query: str,
        media_type: str | None = None,
    ) -> str:
        """
        Recherche du contenu dans Plex par titre, acteur, réalisateur, etc.

        Args:
            query: Terme de recherche (titre, acteur, réalisateur, genre...)
            media_type: Type de média à rechercher (movie, show, episode, artist, album, track). Si non spécifié, recherche tous les types.
        """
        results = await client.search(query, media_type)
        simplified = []
        for r in results[:20]:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "type": r.get("type"),
                "year": r.get("year"),
                "summary": (r.get("summary") or "")[:200] + "..." if len(r.get("summary") or "") > 200 else r.get("summary", ""),
                "rating": r.get("audienceRating"),
                "viewCount": r.get("viewCount", 0),
                "lastViewedAt": r.get("lastViewedAt"),
                "addedAt": r.get("addedAt"),
                "director": [d.get("tag") for d in r.get("Director", [])] if r.get("Director") else None,
                "genre": [g.get("tag") for g in r.get("Genre", [])] if r.get("Genre") else None,
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_unwatched(
        library_key: str | None = None,
        limit: int = 50,
    ) -> str:
        """
        Récupère les films ou séries non vus.

        Args:
            library_key: Clé de la bibliothèque (optionnel, utiliser plex_get_libraries pour trouver les clés)
            limit: Nombre maximum de résultats
        """
        if library_key:
            results = await client.get_library_content(library_key, unwatched_only=True)
        else:
            libraries = await client.get_libraries()
            results = []
            for lib in libraries:
                if lib.get("type") in ["movie", "show"]:
                    content = await client.get_library_content(lib.get("key"), unwatched_only=True)
                    results.extend(content)

        simplified = []
        for r in results[:limit]:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "type": r.get("type"),
                "year": r.get("year"),
                "summary": (r.get("summary") or "")[:150] + "..." if len(r.get("summary") or "") > 150 else r.get("summary", ""),
                "rating": r.get("audienceRating"),
                "addedAt": r.get("addedAt"),
                "genre": [g.get("tag") for g in r.get("Genre", [])] if r.get("Genre") else None,
            })
        return json.dumps({"count": len(simplified), "items": simplified}, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_watched(limit: int = 50) -> str:
        """
        Récupère l'historique de visionnage (films et séries déjà vus).

        Args:
            limit: Nombre maximum de résultats
        """
        results = await client.get_watch_history(limit)
        simplified = []
        for r in results:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "grandparentTitle": r.get("grandparentTitle"),
                "type": r.get("type"),
                "year": r.get("year"),
                "viewedAt": r.get("viewedAt"),
                "accountID": r.get("accountID"),
            })
        return json.dumps({"count": len(simplified), "items": simplified}, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_on_deck() -> str:
        """Récupère les médias 'À suivre' (en cours de visionnage, à reprendre)."""
        results = await client.get_on_deck()
        simplified = []
        for r in results:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "grandparentTitle": r.get("grandparentTitle"),
                "type": r.get("type"),
                "year": r.get("year"),
                "viewOffset": r.get("viewOffset"),
                "duration": r.get("duration"),
                "summary": (r.get("summary") or "")[:150] + "..." if len(r.get("summary") or "") > 150 else r.get("summary", ""),
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_recently_added(limit: int = 30) -> str:
        """
        Récupère les médias récemment ajoutés à la bibliothèque.

        Args:
            limit: Nombre maximum de résultats
        """
        results = await client.get_recently_added(limit)
        simplified = []
        for r in results:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "type": r.get("type"),
                "year": r.get("year"),
                "addedAt": r.get("addedAt"),
                "summary": (r.get("summary") or "")[:150] + "..." if len(r.get("summary") or "") > 150 else r.get("summary", ""),
                "rating": r.get("audienceRating"),
                "genre": [g.get("tag") for g in r.get("Genre", [])] if r.get("Genre") else None,
            })
        return json.dumps(simplified, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_recommendations(rating_key: str) -> str:
        """
        Récupère des recommandations basées sur un film ou une série.

        Args:
            rating_key: L'identifiant du média (obtenu via plex_search ou autres outils)
        """
        source = await client.get_metadata(rating_key)
        source_title = source.get("title", f"ID:{rating_key}")

        results = await client.get_similar(rating_key)
        simplified = []
        for r in results[:15]:
            simplified.append({
                "ratingKey": r.get("ratingKey"),
                "title": r.get("title"),
                "type": r.get("type"),
                "year": r.get("year"),
                "summary": (r.get("summary") or "")[:150] + "..." if len(r.get("summary") or "") > 150 else r.get("summary", ""),
                "rating": r.get("audienceRating"),
            })
        return json.dumps({
            "basedOn": source_title,
            "recommendations": simplified
        }, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_get_movie_details(rating_key: str) -> str:
        """
        Récupère les détails complets d'un film ou d'une série.

        Args:
            rating_key: L'identifiant du média
        """
        metadata = await client.get_metadata(rating_key)
        details = {
            "ratingKey": metadata.get("ratingKey"),
            "title": metadata.get("title"),
            "originalTitle": metadata.get("originalTitle"),
            "type": metadata.get("type"),
            "year": metadata.get("year"),
            "contentRating": metadata.get("contentRating"),
            "summary": metadata.get("summary"),
            "rating": metadata.get("rating"),
            "audienceRating": metadata.get("audienceRating"),
            "duration": metadata.get("duration"),
            "viewCount": metadata.get("viewCount", 0),
            "lastViewedAt": metadata.get("lastViewedAt"),
            "addedAt": metadata.get("addedAt"),
            "studio": metadata.get("studio"),
            "director": [d.get("tag") for d in metadata.get("Director", [])] if metadata.get("Director") else None,
            "writer": [w.get("tag") for w in metadata.get("Writer", [])] if metadata.get("Writer") else None,
            "role": [{"actor": r.get("tag"), "role": r.get("role")} for r in metadata.get("Role", [])[:10]] if metadata.get("Role") else None,
            "genre": [g.get("tag") for g in metadata.get("Genre", [])] if metadata.get("Genre") else None,
            "country": [c.get("tag") for c in metadata.get("Country", [])] if metadata.get("Country") else None,
        }
        return json.dumps(details, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_server_status() -> str:
        """Récupère les informations et le statut du serveur Plex."""
        info = await client.get_server_info()
        sessions = await client.get_active_sessions()

        status = {
            "serverName": info.get("friendlyName"),
            "version": info.get("version"),
            "platform": info.get("platform"),
            "platformVersion": info.get("platformVersion"),
            "myPlex": info.get("myPlex"),
            "activeSessions": len(sessions),
            "currentlyPlaying": [
                {
                    "title": s.get("title"),
                    "grandparentTitle": s.get("grandparentTitle"),
                    "user": s.get("User", {}).get("title") if s.get("User") else None,
                    "player": s.get("Player", {}).get("product") if s.get("Player") else None,
                    "state": s.get("Player", {}).get("state") if s.get("Player") else None,
                }
                for s in sessions
            ],
        }
        return json.dumps(status, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def plex_search_movies(
        library_key: str | None = None,
        actor: str | None = None,
        director: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        min_rating: float | None = None,
        watch_status: str | None = None,
        added_within_days: int | None = None,
        sort_by: str = "audienceRating:desc",
        limit: int = 50,
    ) -> str:
        """
        Recherche avancée de films dans la bibliothèque Plex avec filtres combinés.

        Tous les critères sont combinés avec une logique AND.

        Args:
            library_key: Clé de bibliothèque (optionnel, sinon toutes les bibliothèques de films)
            actor: Nom de l'acteur (ex: "Brad Pitt")
            director: Nom du réalisateur (ex: "Steven Spielberg")
            genre: Genre du film (ex: "Action", "Comedy", "Drama")
            year: Année de sortie exacte (ex: 2023)
            year_min: Année minimum (ex: 2000)
            year_max: Année maximum (ex: 2023)
            min_rating: Note IMDB minimum (ex: 7.0)
            watch_status: "watched", "unwatched", ou None pour tous
            added_within_days: Films ajoutés dans les X derniers jours (ex: 30)
            sort_by: Tri des résultats (audienceRating:desc, addedAt:desc, year:desc, title:asc)
            limit: Nombre maximum de résultats

        Exemples:
            - Films avec Brad Pitt non vus: actor="Brad Pitt", watch_status="unwatched"
            - Comédies bien notées des 5 dernières années: genre="Comedy", year_min=2019, min_rating=7.0
            - Films ajoutés ce mois-ci: added_within_days=30
        """
        # Déterminer les bibliothèques à scanner
        if library_key:
            library_keys = [library_key]
        else:
            libraries = await client.get_libraries()
            library_keys = [
                lib.get("key") for lib in libraries
                if lib.get("type") == "movie"
            ]

        # Déterminer le filtre unwatched
        unwatched_only = watch_status == "unwatched"

        # Récupérer les films depuis toutes les bibliothèques
        all_results = []
        for key in library_keys:
            movies = await client.get_library_content(
                key,
                unwatched_only=unwatched_only,
                actor=actor,
                director=director,
                genre=genre,
                year=year,
                year_min=year_min,
                year_max=year_max,
                min_rating=min_rating,
                added_within_days=added_within_days,
                sort_by=sort_by,
            )
            all_results.extend(movies)

        # Filtrage client-side pour watch_status="watched" (API ne supporte pas directement)
        if watch_status == "watched":
            all_results = [m for m in all_results if m.get("viewCount", 0) > 0]

        # Appliquer la limite
        all_results = all_results[:limit]

        # Simplifier les résultats
        simplified = []
        for m in all_results:
            simplified.append({
                "ratingKey": m.get("ratingKey"),
                "title": m.get("title"),
                "year": m.get("year"),
                "rating": m.get("audienceRating"),
                "viewCount": m.get("viewCount", 0),
                "addedAt": m.get("addedAt"),
                "summary": (m.get("summary") or "")[:150] + "..." if len(m.get("summary") or "") > 150 else m.get("summary", ""),
                "genre": [g.get("tag") for g in m.get("Genre", [])] if m.get("Genre") else None,
                "director": [d.get("tag") for d in m.get("Director", [])] if m.get("Director") else None,
            })

        # Construire les filtres appliqués pour la réponse
        filters_applied = {
            k: v for k, v in {
                "actor": actor,
                "director": director,
                "genre": genre,
                "year": year,
                "year_min": year_min,
                "year_max": year_max,
                "min_rating": min_rating,
                "watch_status": watch_status,
                "added_within_days": added_within_days,
            }.items() if v is not None
        }

        return json.dumps({
            "count": len(simplified),
            "filters_applied": filters_applied,
            "sort_by": sort_by,
            "items": simplified
        }, indent=2, ensure_ascii=False)
