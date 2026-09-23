from pathlib import Path
from typing import Optional, Sequence

from services.lyrics_service import lyrics_service
from services.player_service import engine
from utils.logger import get_logger

logger = get_logger(__name__)


class LyricsController:
    def get_lyrics(self, id_song: int):
        lyrics = lyrics_service.get_lyrics(id_song)
        if lyrics:
            return lyrics
        else:
            logger.debug("Aucune parole pour le morceau %s", id_song)
            return None

    def save_lyrics(self, id_song: int, lyrics: Optional[Sequence[str]] = None, path_lyrics: Optional[Path] = None):
        if lyrics is None:
            logger.warning("Aucune parole à enregistrer pour le morceau %s", id_song)
            return False

        if lyrics_service.save_lyrics(id_song, lyrics):
            logger.info("Parole ajoutée avec succès pour le morceau %s", id_song)
            return True

        logger.error("Echec d'insertion des paroles pour le morceau %s", id_song)
        return False

    def import_lyrics_file(self, file_path: str | Path):
        imported_lines = lyrics_service.import_lyrics_file(str(file_path))
        logger.info("Paroles importées depuis le fichier: %s", file_path)
        return imported_lines

    def edit_lyrics(self, current_content: Sequence[str] | str | None, edited_lines: Sequence[str]):
        result = lyrics_service.edit_lyrics(current_content, edited_lines)
        logger.debug("Paroles modifiées")
        return result

    def generate_manual_sync(self, content: Sequence[str] | str | None, timestamps: Sequence[float]):
        synced = lyrics_service.generate_manual_sync(content, timestamps)
        logger.debug("Synchronisation manuelle générée")
        return synced

    def generate_automatic_sync(self, id_song: int, content: Sequence[str] | str | None):
        """Génère automatiquement la synchronisation LRC d'un morceau à
        partir de ses paroles brutes (sans timestamps), en analysant son
        fichier audio.
        """
        synced = lyrics_service.generate_automatic_sync(id_song, content)
        if synced:
            logger.info("Synchronisation automatique générée pour le morceau %s", id_song)
        else:
            logger.warning(
                "Echec de la synchronisation automatique pour le morceau %s "
                "(audio introuvable ou illisible)", id_song
            )
        return synced

    def get_current_lyric(self, id_song: int, current_time: float) -> str:
        lyric = lyrics_service.get_current_lyric(id_song, current_time)
        if lyric:
            return lyric
        return ""

    def get_parsed_lyrics(self, id_song: int):
        """Paroles synchronisées du morceau, sous forme de liste de lignes
        ``{"time": float, "text": str}`` triées par timestamp. Utilisé par
        la vue des paroles (LyricsView) pour l'affichage et le défilement
        automatique."""
        return lyrics_service.get_parsed_lyrics(id_song)

    def sync_lyrics(self, id_song: int, current_time: float):
        lyric = self.get_current_lyric(id_song, current_time)
        logger.debug("[%.2fs] %s", current_time, lyric)
        return lyric

    def sync_current_lyrics(self, id_song: int | None = None, current_time: float | None = None):
        if id_song is None:
            current_song = engine.current_song()
            if current_song is None:
                return ""
            id_song = current_song.id

        if current_time is None:
            current_time = engine.current_position()

        return self.sync_lyrics(id_song, current_time)

    def remove_lyrics(self, id_song: int) -> bool:
        result = lyrics_service.remove_lyrics(id_song)
        if result:
            logger.info("Paroles supprimées pour le morceau %s", id_song)
        else:
            logger.debug("Aucune parole à supprimer pour le morceau %s", id_song)
        return result

lyrics_controller = LyricsController()
