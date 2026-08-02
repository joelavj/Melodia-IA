from services.directory_service import directory_service
from pathlib import Path

class DirectoryController :

    def add(self, path:str)->None:
        resultat = directory_service.add(Path(path))
        print(resultat[1])
        if resultat[0]:
            pass

    def remove(self, id:int)->None:
        directory_service.remove(id)