from typing import Callable, Optional

from repositories.song_repository import song_repository
from infrastructure.ai.genre_classifier import genre_classifier
from infrastructure.ai.audio_features import AudioFeatureExtractionError


class GenreDetectionService:
    """Détection automatique du genre d'un morceau à partir de son contenu
    audio (voir ``infrastructure/ai/genre_classifier.py`` pour le détail et
    les limites de l'approche utilisée).
    """

    MIN_CONFIDENCE = 0.2

    def detect(self, id_song: int, force: bool = False) -> Optional[str]:
        """Détecte et enregistre le genre du morceau ``id_song``.

        Par défaut (``force=False``), ne fait rien si le morceau a déjà un
        genre renseigné (par ses tags ou une détection précédente).
        """
        song = song_repository.find_by_id(id_song)
        if song is None:
            return None
        if not force and song.genre:
            return song.genre
        if not song.path.exists():
            return None

        try:
            prediction = genre_classifier.predict(song.path)
        except AudioFeatureExtractionError:
            return None

        if prediction.confidence < self.MIN_CONFIDENCE:
            return None

        song_repository.update_genre(id_song, prediction.genre)
        return prediction.genre

    def detect_missing_genres(
        self,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> dict[int, str]:
        """Lance la détection pour tous les morceaux sans genre renseigné.

        ``on_progress(done, total)`` est appelé après chaque morceau traité,
        pour permettre à l'appelant (typiquement une vue) d'afficher une
        progression sur une opération potentiellement longue.

        Retourne un dict {id_morceau: genre_détecté} pour les morceaux
        traités avec succès.
        """
        results: dict[int, str] = {}
        ids = song_repository.find_ids_without_genre()
        total = len(ids)
        for index, id_song in enumerate(ids, start=1):
            genre = self.detect(id_song)
            if genre is not None:
                results[id_song] = genre
            if on_progress is not None:
                on_progress(index, total)
        return results


genre_detection_service = GenreDetectionService()