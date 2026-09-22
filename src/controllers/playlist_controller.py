from services.playlist_service import playlist_service
from services.queue_service import queue

class PlaylistController:
    def create(self,name:str):
        playlist_service.create_playlist(name)

    def play(self, id_playlist:int,id_song:int|None):
        if not playlist_service.play(id_playlist,id_song):
            print("Playlist vide")

    def remove(self,id_playlist:int):
        playlist_service.delete_playlist(id_playlist)

    def add_song(self, id_playlist:int, id_song:int):
        playlist_service.add_song(id_playlist,id_song)

    def remove_song(self, id_playlist:int, id_song:int):
        playlist_service.remove_song(id_playlist,id_song)

playlist_controller = PlaylistController()