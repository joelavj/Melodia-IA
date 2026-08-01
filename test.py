# Importation des controllers
import controllers.directory_controller as directory_controller
import controllers.library_controller as library_controller
import controllers.player_controller as player_contoller
import controllers.queue_controller as queue_controller
# Importation des modèles
from models.directory_model import Directory
from models.song_model import Song
from models.queue_model import Queue
# Importation des autres bibliothèque
from pathlib import Path
from utils.constante import RepeatMode, StatePlay
from typing import cast,Optional

MENU_PRINCIPAL = [
    'Voir les morceaux',
    'Voir les répertoires',
    "Voir la file d'attente",
    'Outils de lecture',
    'Quitter le programme'
]

MENU_MORCEAUX = [
    "Ajouter un morceau à la file d'attente",
    'Lire un morceau'
]

MENU_REPERTOIRES = [
    'Retirer un répertoire',
    'Ajouter un nouveau répertoire',
    'Scanner un répertoire',
    'Scanner tout les répertoires',
    'Actualiser la bibliothèque'
]

MENU_FILE_ATTENTE = [
    "Vider la file d'attente",
    'Lancer un morceau',
    'Retirer un morceau',
]

MENU_LECTURE = [
    "Précédent"
    "Lecture/Pause",
    "Suivant",
    "Stop",
    "Répétition"
]

def afficher_menu_principal():
    print(50*"=", "\n")
    print("Menu principal: ")
    print(50*"=", "\n")
    for (i, menu) in enumerate(MENU_PRINCIPAL, start=1):
            print(f"{i}) {menu}", "\n")
    print(50*"=", "\n")

def afficher_menu_morceau():
    print(50*"=", "\n")
    print("Menu morceau: ")
    print(50*"=", "\n")
    for (i, menu) in enumerate(MENU_MORCEAUX, start=1):
                print(f"{i}) {menu}", "\n")
    print(50*"=", "\n")

def afficher_menu_file_attente():
    print(50*"=", "\n")
    print("Menu file d'attente: ")
    print(50*"=", "\n")
    for (i, menu) in enumerate(MENU_FILE_ATTENTE, start=1):
                print(f"{i}) {menu}", "\n")
    print(50*"=", "\n")

def afficher_menu_repertoire():
    print(50*"=", "\n")
    print("Menu répertoire: ")
    print(50*"=", "\n")
    for (i, menu) in enumerate(MENU_REPERTOIRES, start=1):
                print(f"{i}) {menu}", "\n")
    print(50*"=", "\n")

def afficher__meunu_lecture():
    print(50*"=", "\n")
    print("Menu lecture: ")
    print(50*"=", "\n")
    for (i, menu) in enumerate(MENU_LECTURE, start=1):
                print(f"{i}) {menu}", "\n")
    print(50*"=", "\n")

def main():
    print(50*"=", "\t")
    print("MELODIA IA", "\t")
    print(50*"=", "\n")
    afficher_menu_principal()
    action = int(input("Action à faire: "))
    if action == 1:
        print("ACTION: VOIR TOUT LES MORCEAUX")
        songs = (library_controller.load_library())['songs']
        if songs == []:
            print("Aucun morceau, veuillez ajouter")
        else:
            for song in songs:
                song_tmp = f"{song.id}) {song.title} | {song.path} | "
                for artist_name in song.artist:
                    song_tmp += f"{artist_name} | "
                song_tmp += f"{song.album} | {song.directory.path}"
                print(song_tmp)
                print(10*'-')
        afficher_menu_morceau()
        action = int(input("Enter l'action à faire: "))
        if action == 1:
            print("ACTION: AJOUTER UN MORCEAU DANS LA FILE D'ATTENTE")
            id_morceau = int(input("Entrer l'id du morceau: "))
            for song in songs:
                if id_morceau == song.id:
                    queue_controller.add_song(song)
                    print("Morceau ajouté avec succès dans la file d'attente")
                    break
            else:
                print("Echec de l'ajout du morceau dans la file d'attente")
        elif action == 2:
            print("ACTION: LANCER UN MORCEAU")
            id_morceau = int(input("Entrer l'id du morceau: "))
            for song in songs:
                if id_morceau == song.id:
                    player_contoller.play_pause(song)
                    break    
            else:
                print("Morceau indisponible")
    elif action == 2:
        print("ACTION: VOIR LES REPERTOIRES")
        directories = (library_controller.load_library())["directories"]
        for directory in directories:
             print(f"{directory.id}) {directory.path}")
        afficher_menu_repertoire()
        action = int(input("Entrer votre choix: "))
        if action == 1:
            print("ACTION: SUPPRIMER UN REPERTOIRE")
            id_repertoire = int(input("Entrer l'id du répertoire: "))
            directory_controller.remove_directory(id_repertoire)
        elif action == 2:
            print("ACTION: AJOUTER UN NOUVEAU REPERTOIRE")
            new_directory = input("Entrer le nouveau répertoire: ")
            directory_controller.add_directory(new_directory)
        elif action == 3:
            print("ACTION: SCANNER UN REPERTOIRE")
            id_repertoire = int(input("Entrer l'id du répertoire à scanner: "))
            directory_controller.scan_directory(id_repertoire)
        elif action == 4:
             print("ACTION: SCANNER TOUT LES REPERTOIRES")
             directory_controller.scan_directories()
    elif action == 3:
        print("ACTION: VOIR LA FILE D'ATTENTE")
        queue = (library_controller.load_library())["queue"]
        if queue == []:
            print("Aucun morceau, file d'attente vide")
        else:
            for song in queue:
                song_tmp = f"{song.id}) {song.title} | {song.path} | "
                for artist_name in song.artist:
                    song_tmp += f"{artist_name} | "
                song_tmp += f"{song.album} | {song.directory.path}"
                print(song_tmp)
                print(10*'-')     
        afficher_menu_file_attente()
        action = int(input("Entrer l'action à faire: "))
        if action == 1:
            print("ACTION: VIDER LA FILE D'ATTENTE")
            queue_controller.clear_queue()
        elif action == 2:
            print("ACTION: LANCER UN MORCEAU")
            id_morceau = int(input("Entrer l'id du morceau: "))
            for song in queue:
                if song.id == id_morceau:
                    player_contoller.play_pause(song)
                    break
            else:
                print("Morceau indisponible")
        elif action == 3:
            print("ACTION: RETIRER UN MORCEAU")
            id_morceau = int(input("Entrer l'id du morceau: "))
            for song in queue:
                if song.id == id_morceau:
                    queue_controller.remove_song(song)
                    break
            else:
                print("Morceau indisponible")
    elif action == 4:
        print("ACTION: OUTIL DE LECTURE")
        afficher__meunu_lecture()
        action = int(input("Entrer l'action à faire: "))
        if action == 1:
            print("ACTION: MORCEAU PRECEDENT")
            player_contoller.previous_song()
        elif action == 2:
            print("ACTION: LECTURE/PAUSE")
            player_contoller.play_pause()
        elif action == 3:
            print("ACTION: MORCEAU SUIVANT")
            player_contoller.next_song()
        elif action == 4:
            print("ACTION: ARRETER LECTURE")
            player_contoller.stop()
        elif action == 5:
            print("ACTION: CHANGER MODE DE LECTURE")
            player_contoller.change_repeat_mode()
    elif action == 5:
        print(50*"=", "\t")
        print("FIN", "\t")
        print(50*"=", "\n")
        exit()
    else:
        print("Choix indisponible")

if __name__ == '__main__':
    continuer = True
    while continuer:
        main()