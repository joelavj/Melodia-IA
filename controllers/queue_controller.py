from services.queue_service import queue
from models.song_model import Song
from typing import Optional

class QueueController :
    def add_song(self, song:Song):
        queue.add(song)

    def remove_song(self, song:Song):
        queue.remove(song)

    def clear_queue(self):
        queue.clear()

    

queue_controller = QueueController()

