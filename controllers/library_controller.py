from services.library_service import library_service

class LibraryController :

    def __init__(self) -> None:
        self.load()

    def load(self):
        library_service.load()
        self.directories = library_service.directories
        self.songs = library_service.songs
        self.queue = library_service.queue


library_controller = LibraryController()