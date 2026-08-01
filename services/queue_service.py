from models.song_model import Song
from utils.constante import *
from typing import Optional, cast
from models.queue_model import Queue
import repositories.queue_repository as queue_repository
import services.player_service as player_service
import services.song_service as song_service

def is_song_here(song:Song)->bool:
    if (queue_repository.find_song(song)).id == -1:
        return False
    return True

def add_song(song:Song):
    global queue
    if not is_song_here(song):
        queue_repository.save(song)
    if len(queue.queue) == 0:
        queue.queue = queue_repository.find_all()
        queue.current_index = queue.queue.index(song)
        queue.current_song = queue.queue[queue.current_index]
        
def remove_song(song:Song):
    if is_song_here(song):
        queue_repository.delete(song)

def clear_queue():
    player_service.stop_song()
    queue_repository.clear_all()

def load_queue():
    queue.queue = []
    for song in queue_repository.find_all():
        queue.queue.append(song_service.load_song(song))
