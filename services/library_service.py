from repositories.song_repository import song_repository
from repositories.directory_repository import directory_repository
from repositories.queue_repository import queue_repository
from pathlib import Path

class LibraryService :

    def __init__(self) -> None:
        self.load()


    def _load_directories(self)->list:
        for directory in directory_repository.find_all():
            if (directory.path).exists() and (directory.path).is_dir():
                for other_directory in directory_repository.find_all():
                    if other_directory.id != directory.id and (other_directory.path).is_relative_to(directory.path):
                        directory_repository.delete(directory.id)
        return directory_repository.find_all()
            

    def _load_songs(self)->list:
        for song in song_repository.find_all():
            if (song.path).exists() and (song.path).is_file():
                for song_other in song_repository.find_all():
                    if song_other.id != song.id and (song_other.path).is_relative_to(song.path):
                        song_repository.delete(song.id)
        return song_repository.find_all()

    def _load_queue(self)->list:
        return queue_repository.find_all()

    def load(self):
        self.directories = self._load_directories()
        self.songs = self._load_songs()
        self.queue = self._load_queue()

library_service = LibraryService()