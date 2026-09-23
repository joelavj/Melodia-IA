# Checklist mise en production — Mélod'IA

## Fait dans ce lot

1. **Logging centralisé** — nouveau `src/utils/logger.py` (console + fichier
   rotatif `logs/melodia_ia.log`, niveau réglable via `MELODIA_LOG_LEVEL`).
2. **`print()` remplacés par le logger** dans la couche backend :
   - `controllers/directory_controller.py`
   - `controllers/player_controller.py`
   - `controllers/lyrics_controller.py`
   - `services/scanner_service.py`
   - `services/player_service.py` (le `print(error)` de `_play_current`)
   - `utils/function.py`
3. **Identifiants MySQL sortis du code** — `database/connect.py` lit
   maintenant `MELODIA_DB_USER` / `MELODIA_DB_PASSWORD` / `MELODIA_DB_HOST` /
   `MELODIA_DB_NAME` depuis l'environnement (fallback sur les anciennes
   valeurs si absentes). Voir `.env.example`.
4. `main.py` charge un `.env` optionnel (si `python-dotenv` est installé,
   sinon ignore silencieusement).
5. `.gitignore` : ajout de `logs/` et `.env`.

## À faire toi-même (remplacements identiques, non inclus ici)

Les `print()` restants sont surtout dans la couche **vues** (`src/views/`),
où ils servent de logs de debug console, par ex. :

- `views/lyrics_view.py` : `print(f"[LyricsView] Erreur...")`
- `views/player_bar.py` : `print(f"[PlayerBar] Erreur...")`
- `views/directories_view.py`, `views/genre_maintenance_view.py`,
  `views/*` : `print(f"Erreur pendant le scan : {e}")`, etc.

Le remplacement est mécanique : ajouter `from utils.logger import get_logger`
+ `logger = get_logger(__name__)` en haut du fichier, puis
`print(f"[Widget] Erreur: {e}")` → `logger.error("Erreur: %s", e, exc_info=True)`.
Je n'ai pas touché ces fichiers pour rester focalisé sur la couche métier ;
dis-moi si tu veux que je fasse le même passage sur les vues.

## Autres points production à considérer

- **`src/test.py`** est vide et non versionné dans `.gitignore` (`tests/`
  l'est, mais pas ce fichier à la racine de `src/`) — à supprimer ou à
  remplir.
- **Dépendances non épinglées** (`pyproject.toml`/`requirements.txt`
  utilisent `>=`) : envisager de figer des versions exactes (`pip freeze`)
  pour un build reproductible.
- **Gestion d'erreurs des repositories** : la plupart des méthodes de
  `repositories/*.py` ne catchent pas les erreurs MySQL individuellement
  (seul `connect()` le fait) — une requête qui échoue en cours de route
  laisse la connexion/le curseur potentiellement non fermés. À revoir avec
  un context manager (`with connect() as cnx: ...`) si le connecteur le
  permet, ou des blocs `try/finally`.
- **Secrets** : vérifie qu'aucun `.env` réel ni mot de passe ne sont déjà
  commités dans l'historique Git avant de pousser ces changements.
