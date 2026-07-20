import services.directory_service as directory_service
import controllers.library_controller as library_controller
from pathlib import Path

def add_directory(chemin:str):
    path = Path(chemin)
    resulat = directory_service.add_directory(path)
    if resulat[0]:
        print(resulat[1])
        directory_service.scan_directory(path)
    else:
        print(resulat[1])
    library_controller.load_library()

def remove_directory(id:int):
    print(directory_service.remove_directory(id))
    library_controller.load_library()

def scan_directory(path:Path):
    directory_service.scan_directory(path)
    library_controller.load_library()

def scan_directories():
    directory_service.scan_directories()
    library_controller.load_library()