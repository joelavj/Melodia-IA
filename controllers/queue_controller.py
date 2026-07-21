from models.song_model import Song
import services.queue_service as queue_service
from models.queue_model import Queue


def add_song(song:Song, queue:Queue|None = None):
    return queue_service.add_song(song=song, queue=queue)


def remove_song(queue:Queue, song:Song):
    return queue_service.remove_song(queue,song)


def clear_queue(queue:Queue):
    return queue_service.clear_queue(queue)

