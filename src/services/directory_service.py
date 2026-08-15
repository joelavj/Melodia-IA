from pathlib import Path
from typing import cast
from repositories.directory_repository import directory_repository

class DirectoryService :
    
    def add(self, path:Path)->tuple[int, str]:
        if not path.exists():
            return (-1, f"le {path} n'existe pas")
        if not path.is_dir():
            return (-1, f"le {path} ne correspond pas a  un repertoire")
        if not self._is_here(path):
            return (-1, f"le {path} existe déjà dans le bibliotheque")
        for directory in directory_repository.find_all():
            if self._englobe(path, directory.path):
                return (-1, f"{path} est déjà englobé par des répertoires existant")
        for directory in directory_repository.find_all():
            if self._englobe(directory.path, path):
                print(f"Suppresion du repertoire {directory.path}")
                self.remove(directory.id)
        id_directory = directory_repository.save(path)
        if id_directory == -1:
            return (id_directory, f"echec d'ajout du repertoire {path}")
        return (id_directory, f"ajout avec succes du repertoire {path}")


    def remove(self, id:int):
            directory_repository.delete(id)
            return "repertoire supprimer avec succes"
    

    def _is_here(self, path:Path)->bool:
        for directory in directory_repository.find_all():
            if path.samefile(directory.path):
                return True
        else:
            return False


    def _englobe(self, path:Path, other_path:Path)->bool:
        return path.resolve().is_relative_to(other_path.resolve())


directory_service = DirectoryService()