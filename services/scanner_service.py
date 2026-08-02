from pathlib import Path
from repositories.directory_repository import directory_repository
from services.song_service import song_service
from services.metadata_service import metadata_reader

class ScannerService :

    def _get_mp3_files(self, path:Path)->list:
        return list(path.rglob('*.mp3'))


    def scan_directory(self, id: int):
        directory = directory_repository.find_by_id(id)
        if directory is None:
            return
        for path in self._get_mp3_files(directory.path):
            if not song_service.is_stored(directory.path):
                song_service.add(metadata_reader.extract(directory.path), directory.path, id)


    def scan_directories(self):
        for directory in directory_repository.find_all():
            self.scan_directory(directory.id)
    

scanner_service = ScannerService()