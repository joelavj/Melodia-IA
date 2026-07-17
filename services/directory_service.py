from pathlib import Path
import repositories.directory_repository as directory_repository
import services.song_service as song_service
from services.metadata_service import extract

def add_directory(path:Path):
    if not path.exists():
        return f"le {path} n'existe pas"
    if not path.is_dir():
        return f"le {path} ne correspond pas à un répertoire"
    for directory in directory_repository.findAll():
        path_target = Path(directory[1])
        if path.samefile(path_target):
            return f"{path} déjà existant"
    for directory in directory_repository.findAll():
        path_target = Path(directory[1])
        if path.is_relative_to(path_target):
            return f"le {path} est déjà contenu dans {path_target}"
    for directory in directory_repository.findAll():
        path_target = Path(directory[1])
        if path_target.is_relative_to(path):
            id_repertoire = directory_repository.findByPath(path_target)[0][0]
            remove_directory(id_repertoire)
    id_repertoire = directory_repository.save(path)
    scan_directory(path)
    return f"ajout avec succès de {path}"
    
def remove_directory(id:int):
    directory_repository.delete(id)
    return "repertoire supprimer avec succès"

def get_mp3_files(path:Path)->list:
    return list(path.rglob('*.mp3'))

def scan_directory(path:Path):
    id_directory = (directory_repository.findByPath(path))[0][0]
    for path_file in get_mp3_files(path):
        path_file = Path(path_file)
        if not song_service.isSongStored(path_file):
            song_service.add(extract(path_file), path_file, id_directory)
            # actualiser bibliothèque
    
