from typing import Optional

from repositories.song_repository import song_repository
from infrastructure.ai.genre_classifier import genre_classifier
from infrastructure.ai.audio_features import AudioFeatureExtractionError


class GenreDetectionService:
    """Détection automatique du genre d'un morceau à partir de son contenu
    audio (voir ``infrastructure/ai/genre_classifier.py`` pour le détail et
    les limites de l'approche utilisée).
    """

    # Confiance minimale en dessous de laquelle on préfère ne rien écrire
    # plutôt que de proposer un genre trop incertain.
    MIN_CONFIDENCE = 0.2

    def detect(self, id_song: int, force: bool = False) -> Optional[str]:
        """Détecte et enregistre le genre du morceau ``id_song``.

        Par défaut (``force=False``), ne fait rien si le morceau a déjà un
        genre renseigné (par ses tags ou une détection précédente).
        Retourne le genre détecté, ou None si la détection n'a pas pu être
        effectuée (fichier introuvable/illisible) ou n'était pas nécessaire.
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

    def detect_missing_genres(self) -> dict[int, str]:
        """Lance la détection pour tous les morceaux sans genre renseigné.

        Retourne un dict {id_morceau: genre_détecté} pour les morceaux
        traités avec succès.
        """
        results: dict[int, str] = {}
        for id_song in song_repository.find_ids_without_genre():
            genre = self.detect(id_song)
            if genre is not None:
                results[id_song] = genre
        return results


genre_detection_service = GenreDetectionService()
