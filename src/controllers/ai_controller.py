import threading
from typing import Callable, Optional

from services.genre_detection_service import genre_detection_service


class AiController:

    def detect_genre(self, id_song: int, force: bool = False) -> Optional[str]:
        """Version synchrone (bloquante) — à réserver aux appels hors thread UI."""
        return genre_detection_service.detect(id_song, force=force)

    def detect_missing_genres(self) -> dict[int, str]:
        """Version synchrone (bloquante) — à réserver aux appels hors thread UI."""
        return genre_detection_service.detect_missing_genres()

    def detect_genre_async(
        self,
        id_song: int,
        on_done: Callable[[Optional[str]], None],
        force: bool = False,
        widget=None,
    ) -> None:
        """Lance la détection dans un thread séparé pour ne pas geler l'UI
        (l'analyse audio peut prendre plusieurs secondes).

        Si ``widget`` est fourni (n'importe quel widget Tkinter/CTk encore
        vivant), le callback est remis sur le thread principal via
        ``widget.after`` — seul moyen sûr de toucher l'UI depuis un thread
        en Tkinter. Sans ``widget``, ``on_done`` est appelé directement
        depuis le thread de fond (à éviter si ``on_done`` touche l'UI).
        """
        def _work():
            genre = genre_detection_service.detect(id_song, force=force)
            if widget is not None:
                widget.after(0, lambda: on_done(genre))
            else:
                on_done(genre)

        threading.Thread(target=_work, daemon=True).start()

    def detect_missing_genres_async(
        self,
        on_done: Callable[[dict], None],
        on_progress: Optional[Callable[[int, int], None]] = None,
        widget=None,
    ) -> None:
        """Lance en tâche de fond la détection pour tous les morceaux sans
        genre. Potentiellement long (bibliothèque entière), d'où
        l'exécution hors thread principal et la progression optionnelle.
        """
        def _progress(done, total):
            if on_progress is None:
                return
            if widget is not None:
                widget.after(0, lambda: on_progress(done, total))
            else:
                on_progress(done, total)

        def _work():
            results = genre_detection_service.detect_missing_genres(on_progress=_progress)
            if widget is not None:
                widget.after(0, lambda: on_done(results))
            else:
                on_done(results)

        threading.Thread(target=_work, daemon=True).start()


ai_controller = AiController()