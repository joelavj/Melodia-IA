from repositories.song_repository import song_repository
from repositories.directory_repository import directory_repository
from repositories.playlist_repository import playlist_repository
from repositories.album_repository import album_repository
from repositories.artist_repository import artist_repository

class LibraryService :

    def __init__(self) -> None:
        self.load()

    def load(self):
        self.directories = directory_repository.find_all()
        self.songs = song_repository.find_all()
        self.queue = playlist_repository.get_songs(0)
        self.artists = artist_repository.find_all()
        self.albums = album_repository.find_all()

library_service = LibraryService()