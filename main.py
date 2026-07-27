import controllers.library_controller as library_controller
import controllers.directory_controller as directory_controller
import controllers.player_controller as player_controller
import controllers.queue_controller as queue_controller

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
            