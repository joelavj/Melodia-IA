from services.directory_service import directory_service
from services.scanner_service import scanner_service
from services.library_service import library_service
from utils.logger import get_logger
from pathlib import Path
import os

logger = get_logger(__name__)


class DirectoryController :

    def add(self, path:str)->None:
        result = directory_service.add(Path(path))
        if not isinstance(result, int):
            logger.warning(result)
        else:
            logger.info("Ajout avec succès du répertoire: %s", path)
            self.scan(result)


    def remove(self, id:int)->None:
        if not directory_service.remove(id):
            logger.warning("Erreur de suppression du répertoire (id=%s)", id)
        # Scanner un répertoire

    def scan(self, id:int):
        scanner_service.scan_directory(id)

    def scan_all(self):
        scanner_service.scan_directories()


directory_controller = DirectoryController()
