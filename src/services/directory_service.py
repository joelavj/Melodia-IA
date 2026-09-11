from pathlib import Path
from typing import cast, Literal
from repositories.directory_repository import directory_repository
from utils.function import normalize_path, englobe

class DirectoryService :

    # Ajouter un nouveau répertoire
    def add(self, path:Path)->int | str:
        # Normaliser le chemin
        path = normalize_path(path)
        # Vérifie si le chemin existe
        if not path.exists():
            return f"le {path} n'existe pas"
        # Vérifie si le chemin est un dossier
        if not path.is_dir():
            return f"le {path} ne correspond pas a un repertoire"
        # Vérifie si le chemin existe déjà ou/et le chemin est déjà englobé par d'autre
        for directory in directory_repository.find_all():
            if englobe(path,directory.path):
                return f"{path} est déjà englobé par des répertoires existant"
        # Vérifie si le répertoire n'englobe pas les autres répertoires        
        for directory in directory_repository.find_all():
            if englobe(directory.path, path):
                self.remove(directory.id)
        # Essai d'enregistrer le répertoire dans la BD
        result = directory_repository.save(path) 
        if result == False:
            return f"echec d'ajout du repertoire {path}"
        # Nouveau répertoire ajouté avec succès
        return result

    # Supprimer un répertoire 
    def remove(self, id:int)->bool:
        # Vérifie  si le répertoire existe dans la base de donnée
        if directory_repository.find_by_id(id) is None:
            return False
        # Si oui, on tente de le supprimer
        return directory_repository.delete(id)
    

directory_service = DirectoryService()