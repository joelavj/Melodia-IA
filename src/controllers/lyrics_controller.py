from pathlib import Path
from typing import Optional, Sequence

from services.lyrics_service import lyrics_service
from services.player_service import engine


class LyricsController:
    def get_lyrics(self, id_song: int):
        lyrics = lyrics_service.get_lyrics(id_song)
        if lyrics:
            print(lyrics)
            return lyrics
        else:
            print("Aucun parole pour ce morceau")
            return None

    def save_lyrics(self, id_song: int, lyrics: Optional[Sequence[str]] = None, path_lyrics: Optional[Path] = None):
        if lyrics is None:
            print("Aucune parole à enregistrer")
            return False

        if lyrics_service.save_lyrics(id_song, lyrics):
            print("Parole ajoute avec succès")
            return True

        print("Echec d'insertion du parole")
        return False

    def import_lyrics_file(self, file_path: str | Path):
        imported_lines = lyrics_service.import_lyrics_file(str(file_path))
        print(f"Paroles importées depuis le fichier: {file_path}")
        return imported_lines

    def edit_lyrics(self, current_content: Sequence[str] | str | None, edited_lines: Sequence[str]):
        result = lyrics_service.edit_lyrics(current_content, edited_lines)
        print("Paroles modifiées")
        return result

    def generate_manual_sync(self, content: Sequence[str] | str | None, timestamps: Sequence[float]):
        synced = lyrics_service.generate_manual_sync(content, timestamps)
        print("Synchronisation manuelle générée")
        return synced

    def generate_automatic_sync(self, id_song: int, content: Sequence[str] | str | None):
        """Génère automatiquement la synchronisation LRC d'un morceau à
        partir de ses paroles brutes (sans timestamps), en analysant son
        fichier audio.
        """
        synced = lyrics_service.generate_automatic_sync(id_song, content)
        if synced:
            print("Synchronisation automatique générée")
        else:
            print("Echec de la synchronisation automatique (audio introuvable ou illisible)")
        return synced

    def get_current_lyric(self, id_song: int, current_time: float) -> str:
        lyric = lyrics_service.get_current_lyric(id_song, current_time)
        if lyric:
            return lyric
        return ""

    def sync_lyrics(self, id_song: int, current_time: float):
        lyric = self.get_current_lyric(id_song, current_time)
        print(f"[{current_time:.2f}s] {lyric}")
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


lyrics_controller = LyricsController()