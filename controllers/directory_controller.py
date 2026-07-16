import services.directory_service as directory_service
from pathlib import Path

def add_directory(path:str):
    return directory_service.add_directory(Path(path))

def remove_directory(id:int):
    return directory_service.remove_directory(id)