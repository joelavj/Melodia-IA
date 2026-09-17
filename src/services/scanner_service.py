from pathlib import Path
from repositories.directory_repository import directory_repository
from services.song_service import song_service
from repositories.artist_repository import artist_repository
from repositories.album_repository import album_repository
from infrastructure.metadata.mp3_reader import metadata_reader
from infrastructure.file_scanner import file_scanner
from infrastructure.cover_storage import cover_storage

class ScannerService :

    def __init__(self) -> None:
        self.counters = {}
    # Scanner un répertoire
    def scan_directory(self, id: int):
        self.counters[id] = 0
        # Vérifier si les morceaux dans la base de données existe physiquement
        for (id_song,path_song) in directory_repository.find_path_songs(id):
            if not path_song.exists():
                song_service.remove(id_song)
            else:
                self.counters[id] += 1 
        # Ajoute les morceaux encore non pris en compte
        directory = directory_repository.find_by_id(id)
        if directory is None:
            return 
        for path in file_scanner.mp3(directory.path):
            if not song_service.is_here(path):
                metadata_file = metadata_reader.extract(path)
                song_service.add(metadata_file, id)
                self.counters[id] += 1
        # Supprime les artistes vide
        for artist in artist_repository.find_all():
            if not artist_repository.find_songs(artist.id):
                artist_repository.delete(artist.id)
        # Supprime les albums videCoverStorage
        for album in album_repository.find_all():
            if not album_repository.find_songs(album.id):
                if album.cover_path is not None:
                    cover_storage.delete(album.cover_path)
                album_repository.delete(album.id)
        print(f"Il y a {self.counters[id]} morceaux dans le répertoire {id}")

    def scan_directories(self):
        for directory in directory_repository.find_all():
            self.scan_directory(directory.id)
    

scanner_service = ScannerService()