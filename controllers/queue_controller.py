from models.song_model import Song
import services.queue_service as queue_service
from models.queue_model import Queue


def add_song(song:Song):
    queue_service.add_song(song=song)

def remove_song(song:Song):
    queue_service.remove_song(song)

def clear_queue():
    queue_service.clear_queue()

