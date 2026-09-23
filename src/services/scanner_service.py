from pathlib import Path
from repositories.directory_repository import directory_repository
from services.song_service import song_service
from repositories.artist_repository import artist_repository
from repositories.album_repository import album_repository
from infrastructure.metadata.audio_reader import metadata_reader, UnsupportedAudioFormatError
from infrastructure.file_scanner import file_scanner
from infrastructure.cover_storage import cover_storage
from utils.logger import get_logger

logger = get_logger(__name__)


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
        for path in file_scanner.audio(directory.path):
            if not song_service.is_here(path):
                try:
                    metadata_file = metadata_reader.extract(path)
                except UnsupportedAudioFormatError as error:
                    # Fichier corrompu ou format non décodable : on l'ignore
                    # plutôt que de faire échouer tout le scan du répertoire.
                    logger.warning("Impossible de lire %s : %s", path, error)
                    continue
                song_service.add(metadata_file, id)
                self.counters[id] += 1
        # Supprime les artistes vide
        for artist in artist_repository.find_all():
            if not artist_repository.find_songs(artist.id):
                artist_repository.delete(artist.id)
        # Supprime les albums vide
        for album in album_repository.find_all():
            if not album_repository.find_songs(album.id):
                if album.cover_path is not None:
                    cover_storage.delete(album.cover_path)
                album_repository.delete(album.id)
        logger.info("Il y a %s morceaux dans le répertoire %s", self.counters[id], id)

    def scan_directories(self):
        for directory in directory_repository.find_all():
            self.scan_directory(directory.id)
    

scanner_service = ScannerService()
