from pathlib import Path
from typing import cast
from repositories.directory_repository import directory_repository
from models.directory_model import Directory

class DirectoryService :
    def add(self, path:Path)->tuple[Directory, str]:
        new_directory = Directory(0, Path(path))
        if not path.exists():
            return (new_directory, f"le {path} n'existe pas")
        if not path.is_dir():
            return (new_directory, f"le {path} ne correspond pas a  un repertoire")
        if not self.is_here(path):
            return (new_directory, f"le {path} existe déjà dans le bibliotheque")
        for directory in directory_repository.find_all():
            if self._englobe(path, directory.path):
                return (directory)
        for directory in directory_repository.find_all():
            path_target = directory.path
            if self._englobe(directory.path, path):
                directory = directory_repository.find_by_path(path_target)
                if isinstance(directory, Directory) and isinstance(directory.id, int):
                    id_directory = directory.id
                else:
                    continue
                self.remove(id_directory)
        new_directory.id = directory_repository.save(path)
        if new_directory.id == 0:
            return (new_directory, f"echec d'ajout du repertoire {path}")
        return (new_directory, f"ajout avec succes du repertoire {path}")


    def is_here(self, path:Path)->bool:
        for directory in directory_repository.find_all():
            if path.samefile(directory.path):
                return True
        else:
            return False


    def _englobe(self, path:Path, other_path:Path)->bool:
        return path.resolve().is_relative_to(other_path.resolve())

    def remove(self, id:int):
            directory_repository.delete(id)
            return "repertoire supprimer avec succes"


directory_service = DirectoryService()