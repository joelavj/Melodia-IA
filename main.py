import controllers.library_controller as library_controller
import customtkinter as ctk
import controllers.directory_controller as directory_controller
import controllers.player_controller as player_controller
import controllers.queue_controller as queue_controller
import services.song_service as song_service
import services.queue_service as queue_service
import services.player_service as player_service
from models.song_model import Song
from pathlib import Path

from views.Nav import NavBar
from views.Menu import SideMenu
from views.afficheList import ListDisplay
from views.LireChanson import PlayerBar
from views.BarreAffichier import LyricsPanel

import sys
import argparse

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
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
    # Afficher les donnée
    "Voir la bibliothèque"  
    "Voir tout les morceaux",
    "Voir tout les artistes",
    "Voir tout les albums",
    "Voir la file d'attente",
    "Voir tout les répertoires"
    # Action sur tout l'ensemble
    "Scanner tout les répertoires",
    "Actualiser la bibliothèque",
    # Action sur un répertoire
    "Scanner un répertoire",
    "Supprimer un répertoire",
    # Action sur un morceau
    "Lire un morceau",
    "Ajouter un morceau dans la file d'attente",
    # Action sur un file d'attente
    "Supprimer un morceau de la file d'attente",
    "Vider la file d'attente",
    # Action sur la lecture
    "Mettre en pause",
    "Arrêter la lecture",
    "Lancer le morceau suivant",
    "Lancer le morceau précédent",
    "Changer la mode de lecture"
]

MENU = [
    "Voir la file d'attente",
    "Voir les répertoires",
    "Voir les morceaux",
    "Voir les artistes",
    "Voir les albums"
    "Outil de lecture"
    "Quitter le programme"
]

def queue():
    print(10*"-")
    for song in (library_controller.load_library())["queue"]:
        print(f"song.id","- ")
        print(f"{song.title}","\t")
        for artist in song.artist:
            print(f"{artist.name}"," | ")
        print(f"{song.album.title}","\t")
        print(f"{song.genre}","\t")
        print(f"{song.directory.id}","\t")
        print(f"{song.path}","\n")
    else:
        print("File d'attente vide")
    print(10*"-")
    print("1- Lancer un morceau")
    print("2- Retirer un morceau du file d'attente")
    print("3- Vider la file d'attente")
    print(10*"-")
    action = int(input("Action à faire: "))

def directory():
    print(10*"-")
    for directory in (library_controller.load_library())["directories"]:
        print(f"{directory.id}","- ")
        print(f"{directory.path}","\n")
    print(10*"-")
    print("1- Scanner un répertoire")
    print(10*"-")

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

class MelodiaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mélod'IA — CustomTkinter")
        self.geometry("1200x750")
        self.minsize(900, 600)

        # Conteneur du haut : Nav
        self.nav = NavBar(self, on_toggle_menu=self.toggle_menu, on_search=self.on_search)
        self.nav.pack(side="top", fill="x")

        # Conteneur du milieu : Menu | Liste | Paroles
        body = ctk.CTkFrame(self, fg_color="#181818", corner_radius=0)
        body.pack(side="top", fill="both", expand=True)

        self.menu = SideMenu(body, on_select=self.on_menu_select)
        self.menu.pack(side="left", fill="y")

        self.list_display = ListDisplay(body, on_item_click=self.on_item_click)
        self.list_display.pack(side="left", fill="both", expand=True)

        self.lyrics_panel = LyricsPanel(body, on_rate=self.on_rate)
        self.lyrics_panel.pack(side="right", fill="y")

        # Conteneur du bas : lecteur
        self.player = PlayerBar(
            self,
            on_play_pause=self.on_play_pause,
            on_next=self.on_next,
            on_prev=self.on_prev,
            on_volume_change=self.on_volume_change,
        )
        self.player.pack(side="bottom", fill="x")

    # --- callbacks ---
    def toggle_menu(self):
        self.menu.toggle()

    def on_search(self, query):
        print("Recherche :", query)

    def on_menu_select(self, label):
        print("Section sélectionnée :", label)

    def on_item_click(self, category, item):
        print(f"{category} sélectionné :", item["titre"])
        self.player.set_song(item["titre"], item.get("sous_titre", ""))

    def on_rate(self, note):
        print("Note attribuée :", note)

    def on_play_pause(self, is_playing):
        print("Lecture" if is_playing else "Pause")

    def on_next(self):
        print("Morceau suivant")

    def on_prev(self):
        print("Morceau précédent")

    def on_volume_change(self, value):
        print("Volume :", value)


if __name__ == "__main__":
    app=MelodiaApp()
    app.mainloop()
    main()

    print(50*"=")
    print("\t\t\tMELODIA IA")
    print(50*"=")
    for (num, menu) in enumerate(MENU):
        print(f"{num}- {menu}")
    action = int(input("Entrer votre choix: "))
    match(action):
        case 0:
            queue()
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case 4:
            pass
        case 5:
            pass
        case 6:
            pass
        case ".":
            pass
            