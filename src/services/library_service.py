from repositories.song_repository import song_repository
from repositories.directory_repository import directory_repository
from repositories.playlist_repository import playlist_repository
from repositories.album_repository import album_repository
from repositories.artist_repository import artist_repository
from models.song_model import Song

class LibraryService :

    def list_directories(self)->list:
        return directory_repository.find_all()

    def list_songs(self)->list:
        return song_repository.short_find_all()

    def list_queue(self)->list:
        return playlist_repository.get_songs(0)

    def list_artists(self)->list:
        return artist_repository.find_all()

    def list_albums(self)->list:
        return album_repository.find_all()

    def list_favorite(self)->list:
        return song_repository.get_songs_favorite()

    def list_playlists(self)->list:
        return playlist_repository.find_all()

    def list_songs_playlist(self, id_playlist:int)->list:
        return playlist_repository.get_songs(id_playlist)

    def list_songs_album(self, id_album:int):
        return album_repository.find_songs(id_album)

    def info_song(self, id_song:int)->Song|None:
        return song_repository.find_by_id(id_song)
    
library_service = LibraryService()