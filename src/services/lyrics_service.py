from infrastructure.lyrics_manager import lyrics_manager
from infrastructure.ai.lyrics_aligner import LyricsAlignmentError
from repositories.song_repository import song_repository
from typing import Literal, Sequence


class LyricsService:
    def get_lyrics(self, id_song: int) -> list[str] | Literal[False]:
        path_lyrics = song_repository.get_lyrics_path(id_song)
        if path_lyrics is None:
            return False
        return lyrics_manager.read_file(path_lyrics)

    def get_current_lyric(self, id_song: int, current_time: float) -> str:
        lyrics = self.get_lyrics(id_song)
        if not lyrics:
            return ""
        return lyrics_manager.get_current_lyric(lyrics, current_time)

    def import_lyrics_file(self, path: str | None) -> list[str]:
        if path is None:
            return []
        return lyrics_manager.import_file(path)

    def edit_lyrics(self, current_content: Sequence[str] | str | None, edited_lines: Sequence[str]) -> list[str]:
        return lyrics_manager.edit_lines(current_content, edited_lines)

    def generate_manual_sync(self, content: Sequence[str] | str | None, timestamps: Sequence[float]) -> list[str]:
        return lyrics_manager.generate_manual_sync(content, timestamps)

    def generate_automatic_sync(self, id_song: int, content: Sequence[str] | str | None) -> list[str] | Literal[False]:
        """Génère automatiquement une synchronisation LRC pour les paroles
        brutes ``content`` en s'appuyant sur le fichier audio du morceau
        ``id_song``. Retourne False si le morceau ou son fichier audio est
        introuvable, ou si l'analyse audio a échoué.
        """
        song = song_repository.find_by_id(id_song)
        if song is None or not song.path.exists():
            return False
        try:
            return lyrics_manager.generate_automatic_sync(content, song.path)
        except LyricsAlignmentError:
            return False

    def save_lyrics(self, id_song: int, lyrics: Sequence[str] | None) -> bool:
        if lyrics is None:
            return False

        path_lyrics = song_repository.get_lyrics_path(id_song)
        if path_lyrics is None:
            path_lyrics = lyrics_manager.new_file()
            song_repository.update_lyrics(id_song, path_lyrics)

        if not lyrics_manager.modify_file(path_lyrics, lyrics):
            return False

        return True


lyrics_service = LyricsService()