from models.queue_model import Queue
from models.song_model import Song
from repositories.queue_repository import queue_repository
from utils.constante import RepeatMode
from typing import cast

class QueueService:
    
    def __init__(self) -> None:
        self._queue = Queue()
        self.reload()

    # Recharge les données
    def reload(self):
        self._queue.queue = queue_repository.find_all()
        if self._queue.queue:
            self._queue.current_index = 0
            self._update_current()
        else:
            self._queue.current_index = -1
            self._queue.current_song = None

    # Ajouter un morceau
    def add(self, id_song:int):
        if queue_repository.find_song(id_song) is None:
            queue_repository.save(id_song)
            self.reload()

    # Supprimer un morceau
    def remove(self, id_song:int):
        num_ordre = queue_repository.find_num_ordre_song(id_song)
        if num_ordre == -1:
            return
        queue_repository.delete(id_song)
        queue_repository.update_order(num_ordre)
        self.reload()

    # Changer l'ordre des morceaux
    def change_order_song(self, id_song:int, pos_init:int, pos_target:int):
        if  not (0 <= pos_init < len(self._queue.queue) and  0 <= pos_target < len(self._queue.queue)):
            print(f"Position incorrect: 0 <= {pos_target} < {len(self._queue.queue)} ==> {0 <= pos_target < len(self._queue.queue)}")
            return # position incorrect
        if pos_init < pos_target:
            # Déplacer vers le bas
            print("Je me déplace vers le bas")
            queue_repository.delete(id_song)
            queue_repository.update_order(pos_init,pos_target)
        elif pos_init > pos_target:
            # Déplacer vers le haut
            print("Je me déplace vers le haut")
            queue_repository.delete(id_song)
            queue_repository.update_order(pos_target,pos_init,False)
        else:
            print("Il y a erreur de position")
            return # pos_init == pos_target
        print("Je m'enregistre")
        queue_repository.save(id_song,num_order=pos_target)

    # Vider la file d'attente
    def clear(self):
        queue_repository.clear_all()
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
        if self.is_empty:
            return None
        if self._queue.current_index == 0:
            return self.current()
        self._queue.current_index -= 1
        self._update_current()
        return self.current()

    def contains(self, song:Song)->bool:
        return queue_repository.find_id_song(song) != -1

    def select(self, song)->Song|None:
        for index, current in enumerate(self._queue.queue):
            if song.id == current.id:
                self._queue.current_index = index
                self._update_current()
                return current
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
        self._queue.current_song = self._queue.queue[self._queue.current_index]



queue = QueueService()
        