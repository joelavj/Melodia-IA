from models.song_model import Song
from utils.constante import *
from typing import Optional, cast
from models.queue_model import Queue
import repositories.queue_repository as queue_repository
import services.song_service as song_service

queue = Queue()

def is_song_here(song:Song)->bool:
    if queue_repository.find_song(song) == -1:
        return False
    return True

def add_song(song:Song):
    global queue
    if not is_song_here(song):
        queue_repository.save(song)
    queue.queue = queue_repository.find_all()
    if len(queue.queue) <= 1:
        queue.current_index = 0
        queue.current_song = queue.queue[queue.current_index]
    else:
        for (tmp, song_tmp) in enumerate(queue.queue):
            if song_tmp.id == song.id:
                current_index = tmp
                current_song = song
        else:
            from services.player_service import play_song
            play_song()
        
def remove_song(song:Song):
    if is_song_here(song):
        queue_repository.delete(song)

def clear_queue():
    import services.player_service as player_service
    player_service.stop_song()
    queue_repository.clear_all()

def load_queue():
<<<<<<< HEAD
    queue.queue = []
    for song in queue_repository.find_all():
        queue.queue.append(song_service.load_song(song))
=======
    return queue_repository.find_all()
>>>>>>> 435b7723e870beebedfec899b61cb68160bdd538
