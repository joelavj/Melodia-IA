from services.genre_detection_service import genre_detection_service


class AiController:

    def detect_genre(self, id_song: int, force: bool = False):
        genre = genre_detection_service.detect(id_song, force=force)
        if genre is not None:
            print(f"Genre détecté pour le morceau {id_song} : {genre}")
        else:
            print(f"Impossible de détecter le genre du morceau {id_song}")
        return genre

    def detect_missing_genres(self):
        results = genre_detection_service.detect_missing_genres()
        print(f"{len(results)} morceau(x) mis à jour avec un genre détecté automatiquement")
        return results


ai_controller = AiController()
