import controllers.directory_controller as directory_controller
import controllers.library_controller as library_controller
import controllers.queue_controller as queue_controller
import controllers.player_controller as player_controller
import services.song_service as song_service
import services.queue_service as queue_service
import services.player_service as player_service
from models.song_model import Song
from pathlib import Path
import sys
import argparse

# Le script fonctionne en deux modes : 'live' (utilise la BD et pygame)
# ou 'demo' si une erreur survient (pas de DB/pygame). Le mode demo
# simule la bibliothèque et la lecture en mémoire pour une démonstration CLI.
DEMO_MODE = False


def _format_artists(artists):
    if not artists:
        return "Artiste inconnu"
    names = []
    for artist in artists:
        if isinstance(artist, str):
            value = artist.strip()
        elif artist is None:
            continue
        else:
            value = getattr(artist, "name", None)
            if value is None:
                value = str(artist)
        if value:
            names.append(str(value).strip())
    return ", ".join(names) if names else "Artiste inconnu"


# Forcer le mode via CLI si demandé
def _parse_cli_for_demo():
    global DEMO_MODE
    try:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--demo", action="store_true")
        parser.add_argument("--live", action="store_true")
        args, _ = parser.parse_known_args()
        if args.demo:
            DEMO_MODE = True
        elif args.live:
            DEMO_MODE = False
    except Exception:
        pass

# Forcer la sortie en UTF-8 pour éviter UnicodeEncodeError sur Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


_parse_cli_for_demo()


class DemoPlayer:
    def __init__(self):
        self.queue: list[Song] = []
        self.current_index: int = -1
        self.current_song: Song | None = None
        self.state = "STOP"

    def add_song(self, song: Song):
        if song in self.queue:
            self.queue.remove(song)
        self.queue.append(song)
        if self.current_song is None:
            self.current_index = 0
            self.current_song = song

    def play(self):
        if not self.queue:
            print("File d'attente vide.")
            return
        if self.current_song is None:
            self.current_index = 0
            self.current_song = self.queue[0]
        self.state = "PLAY"
        print(f"Lecture: {self.current_song.title}")

    def pause(self):
        if self.state == "PLAY":
            self.state = "PAUSE"
            print("Lecture mise en pause.")

    def stop(self):
        self.state = "STOP"
        print("Lecture arrêtée.")

    def next(self):
        if not self.queue:
            return
        self.current_index = (self.current_index + 1) % len(self.queue)
        self.current_song = self.queue[self.current_index]
        self.play()

    def previous(self):
        if not self.queue:
            return
        self.current_index = (self.current_index - 1) % len(self.queue)
        self.current_song = self.queue[self.current_index]
        self.play()


demo_player = DemoPlayer()
demo_songs: list[Song] = [
    Song(id=1, title="Demo Track 1", artist=["Artiste A"], genre="Pop", path=Path("/tmp/demo1.mp3")),
    Song(id=2, title="Demo Track 2", artist=["Artiste B"], genre="Rock", path=Path("/tmp/demo2.mp3")),
]

def ensure_mode():
    global DEMO_MODE
    if DEMO_MODE:
        return
    try:
        # tentative d'accès à la bibliothèque pour détecter une DB fonctionnelle
        # Vérifier la connexion MySQL directement (évite d'exécuter tout le chargement)
        from database import connect as db_connect
        cnx = db_connect.connect()
        cnx.close()
    except ConnectionError as ce:
        DEMO_MODE = True
        print("Mode DEMO activé : impossible de se connecter à la base de données.", ce)
    except Exception as e:
        # Ne pas forcer le mode demo pour toute erreur non liée à la connexion.
        print("Avertissement lors du test de la bibliothèque (mode live conservé):", e)

MENU = [
    "Afficher la bibliothèque",
    "Ajouter un répertoire",
    "Scanner tous les répertoires",
    "Afficher la file d'attente",
    "Ajouter un morceau à la file d'attente",
    "Jouer / Reprendre",
    "Mettre en pause",
    "Arrêter la lecture",
    "Morceau suivant",
    "Morceau précédent",
    "Quitter",
]


def display_library():
    ensure_mode()
    if DEMO_MODE:
        print("\n=== BIBLIOTHÈQUE (DEMO) ===")
        print("Répertoires:\n - /music/demo")
        print("Morceaux:")
        for s in demo_songs:
            print(f"{s.id} - {s.title} ({s.genre}) - {_format_artists(s.artist or [])}")
        return
    library = library_controller.load_library()
    if not library:
        print("Aucune bibliothèque chargée.")
        return
    for section in library:
        for key, value in section.items():
            print(f"\n=== {key.upper()} ===")
            if not value:
                print("Aucun élément.")
                continue
            for item in value:
                print(item)


def display_queue():
    print("\n=== FILE D'ATTENTE ===")
    ensure_mode()
    if DEMO_MODE:
        if not demo_player.queue:
            print("File d'attente vide.")
            return
        for index, song in enumerate(demo_player.queue, start=1):
            current = " <= en cours" if demo_player.current_song and song.id == demo_player.current_song.id else ""
            print(f"{index}. {song.title} - {_format_artists(song.artist or [])}{current}")
        return
    active_queue = queue_service.get_active_queue()
    if not active_queue.queue:
        print("File d'attente vide.")
        return
    for index, song in enumerate(active_queue.queue, start=1):
        current = " <= en cours" if active_queue.current_song and song.id == active_queue.current_song.id else ""
        print(f"{index}. {song.title} - {_format_artists(song.artist or [])}{current}")


def choose_song_to_queue():
    ensure_mode()
    if DEMO_MODE:
        print("Morceaux disponibles (DEMO):")
        for s in demo_songs:
            print(f"{s.id} - {s.title} ({s.genre})")
        try:
            song_id = int(input("Entrez l'id du morceau à ajouter à la file: "))
        except ValueError:
            print("Entrée invalide.")
            return
        selected = [song for song in demo_songs if song.id == song_id]
        if not selected:
            print("Morceau introuvable.")
            return
        song = selected[0]
        demo_player.add_song(song)
        print(f"Morceau ajouté: {song.title}")
        return
    songs = song_service.load_songs()
    if not songs:
        print("Aucun morceau disponible.")
        return
    for song in songs:
        print(f"{song[0]} - {song[1]} ({song[3]})")
    try:
        song_id = int(input("Entrez l'id du morceau à ajouter à la file: "))
    except ValueError:
        print("Entrée invalide.")
        return
    selected = [song for song in songs if song[0] == song_id]
    if not selected:
        print("Morceau introuvable.")
        return
    row = selected[0]
    song = Song(
        id=row[0],
        title=row[1],
        artist=[],
        album=None,
        genre=row[3] if len(row) > 3 else "",
        path=Path(row[2]) if len(row) > 2 and row[2] else Path(""),
    )
    queue_controller.add_song(song)
    print(f"Morceau ajouté: {song.title}")
    display_queue()


def input_directory():
    chemin = input("Chemin du répertoire à ajouter: ")
    ensure_mode()
    if DEMO_MODE:
        print(f"(DEMO) Répertoire ajouté: {chemin}")
        return
    directory_controller.add_directory(chemin)


def main():
    while True:
        print("\n" + "=" * 50)
        print("\t\tMELODIA IA - CLI")
        print("=" * 50)
        for index, label in enumerate(MENU, start=1):
            print(f"{index}. {label}")
        try:
            action = int(input("Choisissez une action: "))
        except ValueError:
            print("Entrée invalide.")
            continue

        if action == 1:
            display_library()
        elif action == 2:
            input_directory()
        elif action == 3:
            directory_controller.scan_directories()
        elif action == 4:
            display_queue()
        elif action == 5:
            choose_song_to_queue()
        elif action == 6:
            ensure_mode()
            if DEMO_MODE:
                demo_player.play()
            else:
                queue = player_controller.play()
                if queue is None:
                    print("Aucune piste à lire. Ajoutez d’abord un morceau à la file d’attente.")
                else:
                    print(f"Lecture lancée sur la file active: {queue.current_song.title if queue.current_song else '—'}")
        elif action == 7:
            ensure_mode()
            if DEMO_MODE:
                demo_player.pause()
            else:
                player_controller.pause()
                print("Lecture mise en pause.")
        elif action == 8:
            ensure_mode()
            if DEMO_MODE:
                demo_player.stop()
            else:
                player_controller.stop()
                print("Lecture arrêtée.")
        elif action == 9:
            ensure_mode()
            if DEMO_MODE:
                demo_player.next()
            else:
                player_service.next_song()
                print("Piste suivante.")
        elif action == 10:
            ensure_mode()
            if DEMO_MODE:
                demo_player.previous()
            else:
                player_service.previous_song()
                print("Piste précédente.")
        elif action == 11:
            print("Au revoir.")
            break
        else:
            print("Action indisponible")


if __name__ == "__main__":
    main()
