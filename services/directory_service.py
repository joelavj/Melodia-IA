from pathlib import Path
import repositories.directory_repository as directory_repository
import services.song_service as song_service
from services.metadata_service import extract
from models.directory_model import Directory

def add_directory(path:Path)->tuple:
    if not path.exists():
        return (False, f"le {path} n'existe pas")
    if not path.is_dir():
        return (False, f"le {path} ne correspond pas Ã  un rÃ©pertoire")
    for directory in directory_repository.find_all():
        path_target = directory.path
        if isinstance(path_target, Path) and path.samefile(path_target):
            return (False, f"{path} dÃ©jÃ  existant")
    for directory in directory_repository.find_all():
        path_target = directory.path
        if isinstance(path_target, Path) and path.is_relative_to(path_target):
            return (False, f"le {path} est dÃ©jÃ  contenu dans {path_target}")
    for directory in directory_repository.find_all():
        path_target = directory.path
        if isinstance(path_target, Path) and path_target.is_relative_to(path):
            directory = directory_repository.find_by_path(path_target)
            if isinstance(directory, Directory) and isinstance(directory.id, int):
                id_directory = directory.id
            else:
                continue
            remove_directory(id_directory)
    if directory_repository.save(path) == 0:
        return (False, f"Ã©chec d'ajout du repertoire {path}")
    return (True, f"ajout avec succÃ¨s du rÃ©pertoire {path}")
    
def remove_directory(id:int):
    directory_repository.delete(id)
    return "repertoire supprimer avec succes"

def get_mp3_files(path:Path)->list:
    return list(path.rglob('*.mp3'))

def scan_directory(path:Path):
    directory = directory_repository.find_by_path(path)
    if isinstance(directory, Directory) and isinstance(directory.id, int):
        id_directory = directory.id
        for path_file in get_mp3_files(path):
            path_file = Path(path_file)
            if not song_service.is_song_stored(path_file):
                song_service.add_song(extract(path_file), path_file, id_directory)

def scan_directories():
    for directory in directory_repository.find_all():
        if isinstance(directory, Directory) and isinstance(directory.path, Path):
            scan_directory(Path(directory.path))

def load_directories()->list[Directory]:
    for directory in directory_repository.find_all():
        if isinstance(directory, Directory) and isinstance(directory.path, Path) and not Path(directory.path).exists() and isinstance(directory.id, int):
            directory_repository.delete(directory.id)
    return directory_repository.find_all()

