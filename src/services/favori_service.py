from repositories.song_repository import song_repository
from services.queue_service import queue
from services.player_service import engine

class FavoriService:
    def add_favori(self, id_song:int):
        if song_repository.short_find_by_id(id_song) is not None:
            song_repository.update_favori(id_song,True)

    def remove_favori(self, id_song:int):
        if song_repository.short_find_by_id(id_song) is not None:
            song_repository.update_favori(id_song,False)

    def play(self,id_song:int|None):
        songs = song_repository.get_songs_favorite()
        if songs:
            queue.clear()
            for song in songs:
                queue.add(song.id)
            engine.play(id_song)

favori_service = FavoriService()
    