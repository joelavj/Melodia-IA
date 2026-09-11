from models.queue_model import Queue
from models.song_model import Song,SongSummary
from utils.constante import RepeatMode
from typing import cast
from repositories.playlist_repository import playlist_repository
from repositories.song_repository import song_repository

class QueueService:
    
    def __init__(self) -> None:
        if not playlist_repository.playlist_is_here("queue"):
            playlist_repository.create_queue()
        self._queue = Queue()
        self.reload()

    # Recharge les données
    def reload(self):
        self._queue.queue = playlist_repository.get_songs(0)
        if self._queue.queue:
            self._queue.current_index = 0
            self._update_current()
        else:
            self._queue.current_index = -1
            self._queue.current_song = None

    # Ajouter un morceau
    def add(self, id_song:int):
        if not playlist_repository.song_is_here(0,id_song):
            playlist_repository.save(0,id_song)
            self.reload()

    # Supprimer un morceau
    def remove(self, id_song:int):
        playlist_repository.clear_playlist(0)
        self._queue.queue = [ song for song in self._queue.queue if song.id!=id_song ]
        for song in self._queue.queue:
            playlist_repository.save(0,song.id)
        self.reload()

    # Vider la file d'attente
    def clear(self):
        playlist_repository.clear_playlist(0)
        self.reload()

    # Obtenir le morceau courant
    def current(self):
        return self._queue.current_song

    # La liste de morceau dans la file d'atente
    def songs(self):
        return self._queue.queue

    # Vérifie si la file d'attente est vide
    def is_empty(self):
        return len(self._queue.queue) == 0

    # Le morceau suivant
    def next(self):
        if self.is_empty():
            return None
        if self._queue.current_index + 1 >= len(self._queue.queue):
            return None
        self._queue.current_index += 1
        self._update_current()
        return self._queue.current_song

    # Le morceau précédent
    def previous(self):
        if self.is_empty():
            return None
        if self._queue.current_index == 0:
            return self.current()
        self._queue.current_index -= 1
        self._update_current()
        return self.current()

    def contains(self, song:Song)->bool:
        return playlist_repository.song_is_here(0,song.id)

    def select(self, song)->Song|None:
        self.reload()
        for index, current in enumerate(self._queue.queue):
            if song.id == current.id:
                self._queue.current_index = index
                self._update_current()
                return self._queue.current_song

        return None

    def has_next(self):
        return self._queue.current_index < len(self._queue.queue) - 1

    def last(self):
        return len(self._queue.queue) - 1

    def select_first(self)->Song|None:
        if self.is_empty():
            return None
        self._queue.current_index = 0
        self._update_current()
        return self._queue.current_song

    def has_previous(self)->bool:
        return self._queue.current_index > 0

    def select_last(self)->Song|None:
        if self.is_empty():
            return None
        self._queue.current_index = len(self._queue.queue) - 1
        self._update_current()

    def _update_current(self):
        if self.is_empty():
            self._queue.current_song = None
            self._queue.current_index = -1
            return
        id_current_song = self._queue.queue[self._queue.current_index].id
        self._queue.current_song = song_repository.find_by_id(id_current_song) 

    def change_order_song(self, id_song:int, pos_init:int, pos_target:int):
        song = self._queue.queue.pop(pos_init)
        self._queue.queue.insert(pos_target,song)
        playlist_repository.clear_playlist(0)
        for song in self._queue.queue:
            playlist_repository.save(0,song.id)
        self.reload()

queue = QueueService()
        