from services.directory_service import directory_service
from services.scanner_service import scanner_service
from services.library_service import library_service
from pathlib import Path
import os

class DirectoryController :

    def add(self, path:str)->None:    
        result = directory_service.add(Path(path))
        if not isinstance(result, int):
            print(result)
        else:
            print(f"Ajout avec succès du répertoire: {path}")
            self.scan(result)


    def remove(self, id:int)->None:
        if not directory_service.remove(id):
            print("Erreur de suppression du répertoire")
        # Scanner un répertoire

    def scan(self, id:int):
        scanner_service.scan_directory(id)

    def scan_all(self):
        scanner_service.scan_directories()


directory_controller = DirectoryController()