from controllers.directory_controller import directory_controller
from controllers.library_controller import library_controller
from controllers.queue_controller import queue_controller
from controllers.player_controller import player_controller

path = r"C:\Users\lathi\Desktop\Alahady hatramin'ny Alahady, Ratsilahy"
directory_controller.add(path)

input("Je lance le scan...")
directory_controller.scan_all()
input("Je lance le scan...")

print(library_controller.list_albums())
print(library_controller.list_artists())
print(library_controller.list_songs())
id_song = int(input("Entrer l'id du morceau:"))
queue_controller.add_song(id_song)
input("Lancer la lecture..")
player_controller.play_song()
input("... J'attend")
