from services.directory_service import directory_service
from services.scanner_service import scanner_service
from services.library_service import library_service
from pathlib import Path

class DirectoryController :

    def add(self, path:str)->None:
        new_directory, resultat = directory_service.add(Path(path))
        print(resultat[1])
        if new_directory.id != 0:
            scanner_service.scan_directory(new_directory.id)
            library_service.load()


    def remove(self, id:int)->None:
        directory_service.remove(id)
        library_service.load()


    def scan(self, id:int):
        scanner_service.scan_directory(id)
        library_service.load()

    def scan_all(self):
        scanner_service.scan_directories()
        library_service.load()


directory_controller = DirectoryController()