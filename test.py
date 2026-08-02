from controllers.directory_controller import directory_controller
from controllers.player_controller import player_controller
from controllers.library_controller import library_controller
from controllers.queue_controller import queue_controller

path = input("Ajouter un nouveau répetoire: ")
directory_controller.add(path)
print("Voici les répertoires: ")
print(library_controller.directories)
print("Voici les morceaux: ")
print("Voici les morceaux: ")
print(library_controller.songs)
print("Voici la file d'attente: ")
print(library_controller.queue)
print("Je lance la lecture")
player_controller.play_song()
input("...Appuyer pour mettre en pause")
player_controller.play_song()
input("Appuyer pour relancer la lecture")
player_controller.play_song()
input("Appuyer pour nexter")
player_controller.next_song()
input("Appuyer pour arreter le chanson")
player_controller.stop_play()
print("Fin")