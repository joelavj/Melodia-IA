import controllers.directory_controller as directory_controller
import controllers.library_controller as library_controller
import controllers.queue_controller as queue_controller
import controllers.player_controller as player_controller
import services.song_service as song_service
import services.queue_service as queue_service
import services.player_service as player_service
from models.song_model import Song
from pathlib import Path

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
    if not queue_service.queue:
        print("File d'attente vide.")
        return
    for index, song in enumerate(queue_service.queue, start=1):
        current = " <= en cours" if queue_service.current_song and song.id == queue_service.current_song.id else ""
        print(f"{index}. {song.title} - {', '.join(song.artist)}{current}")


def choose_song_to_queue():
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
        album="",
        genre=row[3] if len(row) > 3 else "",
        path=Path(row[2]) if len(row) > 2 and row[2] else Path(""),
    )
    queue_controller.add_song(song)
    print(f"Morceau ajouté: {song.title}")


def input_directory():
    chemin = input("Chemin du répertoire à ajouter: ")
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
            player_controller.play()
        elif action == 7:
            player_controller.play()
        elif action == 8:
            player_controller.stop()
        elif action == 9:
            player_service.next_song()
        elif action == 10:
            player_service.previous_song()
        elif action == 11:
            print("Au revoir.")
            break
        else:
            print("Action indisponible")


if __name__ == "__main__":
    main()
