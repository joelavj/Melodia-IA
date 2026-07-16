from pathlib import Path
from repositories.directory_repository import findAll, save, delete

def add_directory(path:Path):
    if not path.exists():
        return f"le {path} n'existe pas"
    if not path.is_dir():
        return f"le {path} ne correspond pas à un répertoire"
    for directory in findAll():
        path_target = Path(directory[1])
        if path.samefile(path_target):
            return f"{path} déjà existant"
    for directory in findAll():
        path_target = Path(directory[1])
        if path.is_relative_to(path_target):
            return f"le {path} est déjà contenu dans {path_target}"
    for directory in findAll():
        path_target = Path(directory[1])
        if path_target.is_relative_to(path):
            # supprimer le repertoire
            pass
    id_repertoire = save(path)
    return f"ajout avec succès de {path}"
    # On règle les conséquences après
    
def remove_directory(id:int):
    delete(id)
    return "repertoire supprimer avec succès"