from services.queue_service import queue
from models.song_model import Song
from typing import Optional

def add_song(song:Song):
    queue.add(song)

def remove_song(song:Song):
    queue.remove(song)

def clear_queue():
    queue.clear()


