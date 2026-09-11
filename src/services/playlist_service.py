from models.playlist_model import Playlist
from repositories.playlist_repository import playlist_repository
from services.queue_service import queue
from services.player_service import engine

class PlaylistService:

    def create_playlist(self,name:str)->bool:
        if playlist_repository.playlist_is_here(name):
            return False
        if playlist_repository.create_playlist(name) == 0:
            return False
        return True

    def delete_playlist(self,id_playlist:int):
        playlist_repository.delete_playlist(id_playlist)

    def add_song(self, id_playlist:int, id_song:int):
        if not playlist_repository.song_is_here(id_playlist,id_song):
            playlist_repository.save(id_playlist,id_song)

    def remove_song(self, id_playlist:int, id_song:int):
        if playlist_repository.song_is_here(id_playlist,id_song):
            playlist_repository.delete_song(id_playlist,id_song)

    def rename_playlist(self, id_playlist:int, name:str):
        if playlist_repository.playlist_is_here(name):
            return False
        playlist_repository.rename_playlist(id_playlist,name)

    def change_order_song(self, id_playlist:int, id_song:int, pos_init:int, pos_target:int):
            songs = playlist_repository.get_songs(id_playlist)
            if songs == []:
                return
            song_move = songs.pop(pos_init)
            songs.insert(pos_target,song_move)
            playlist_repository.clear_playlist(id_playlist)
            for song in songs:
                playlist_repository.save(id_playlist,song.id)

    def play(self, id_playlist:int,id_song:int|None):
        songs = playlist_repository.get_songs(id_playlist)
        if songs:
            queue.clear()
            for song in songs:
                queue.add(song.id)
            engine.play(id_song)        
            return True
        return False

    
playlist_service = PlaylistService()