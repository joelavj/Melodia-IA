from models.song_model import Song
from utils.constante import *
from typing import Optional
from models.queue_model import Queue
import repositories.queue_repository as queue_repository

ACTIVE_QUEUE = Queue(name="active")

def _create(nom:str)->Queue:
    queue = Queue(name=nom)
    queue = queue_repository.create(queue)
    return queue

def get_active_queue()->Queue:
    return ACTIVE_QUEUE

def reset_queue()->None:
    global ACTIVE_QUEUE
    ACTIVE_QUEUE = Queue(name="active")

def add_song(song:Song, queue:Optional[Queue]=None)->Queue:
    global ACTIVE_QUEUE
    target_queue = queue or ACTIVE_QUEUE
    if target_queue.id == -1:
        target_queue = _create(song.title)
        ACTIVE_QUEUE = target_queue
    target_queue.add_song(song)
    ACTIVE_QUEUE = target_queue
    return target_queue

def remove_song(queue:Queue, song:Song)->Queue:
    queue.remove_song(song)
    return queue

def clear_queue(queue:Queue)->Queue:
    queue.clear_queue()
    return queue


